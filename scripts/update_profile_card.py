#!/usr/bin/env python3
"""
Generate the dual-theme GitHub profile card from live GitHub data.

The script intentionally uses only Python's standard library so the workflow
does not need pip dependencies.
"""

from __future__ import annotations

import html
import json
import os
import re
import sys
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

USERNAME = "kauntiaakash2"
API_VERSION = "2026-03-10"
ROOT = Path(__file__).resolve().parents[1]
FILES = {
    "dark": ROOT / "dark_mode.svg",
    "light": ROOT / "light_mode.svg",
}


def api_request(url: str, payload: dict | None = None) -> dict:
    token = os.getenv("PROFILE_TOKEN") or os.getenv("GITHUB_TOKEN")
    if not token:
        raise RuntimeError("GITHUB_TOKEN/PROFILE_TOKEN is not set")

    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {token}",
        "X-GitHub-Api-Version": API_VERSION,
        "User-Agent": f"{USERNAME}-profile-card-generator",
    }

    data = None
    if payload is not None:
        headers["Content-Type"] = "application/json"
        data = json.dumps(payload).encode("utf-8")

    request = Request(url, data=data, headers=headers, method="POST" if data else "GET")
    try:
        with urlopen(request, timeout=30) as response:
            return json.load(response)
    except HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"GitHub API {exc.code} for {url}: {body}") from exc
    except URLError as exc:
        raise RuntimeError(f"GitHub API request failed for {url}: {exc}") from exc


def graphql(query: str, variables: dict) -> dict:
    result = api_request(
        "https://api.github.com/graphql",
        {"query": query, "variables": variables},
    )
    if result.get("errors"):
        raise RuntimeError("GraphQL errors: " + json.dumps(result["errors"]))
    return result["data"]


QUERY = """
query($login: String!, $from: DateTime!, $to: DateTime!) {
  user(login: $login) {
    login
    createdAt
    followers { totalCount }
    repositories(first: 100, ownerAffiliations: OWNER, privacy: PUBLIC) {
      totalCount
      nodes {
        name
        nameWithOwner
        isFork
        stargazerCount
        forkCount
        languages(first: 20, orderBy: {field: SIZE, direction: DESC}) {
          edges {
            size
            node { name }
          }
        }
      }
    }
    contributionsCollection(from: $from, to: $to) {
      totalContributions
      totalCommitContributions
      totalIssueContributions
      totalPullRequestContributions
      totalPullRequestReviewContributions
      restrictedContributionsCount
      totalRepositoriesWithContributedCommits
      contributionCalendar {
        weeks {
          contributionDays {
            date
            contributionCount
          }
        }
      }
    }
  }
}
"""


def search_count(query: str, endpoint: str = "https://api.github.com/search/issues") -> int:
    encoded = __import__("urllib.parse", fromlist=["urlencode"]).urlencode(
        {"q": query, "per_page": 1}
    )
    result = api_request(f"{endpoint}?{encoded}")
    return int(result.get("total_count", 0))


def add_years(dt: datetime, years: int) -> datetime:
    try:
        return dt.replace(year=dt.year + years)
    except ValueError:
        # Feb 29 -> Feb 28 on non-leap anniversaries.
        return dt.replace(year=dt.year + years, month=2, day=28)


def format_uptime(created_at: str, now: datetime) -> str:
    created = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
    years = max(0, now.year - created.year)
    anniversary = add_years(created, years)
    if anniversary > now:
        years -= 1
        anniversary = add_years(created, years)
    days = max(0, (now - anniversary).days)
    return f"{years} years, {days} days"


def format_languages(repositories: list[dict]) -> str:
    sizes = Counter()
    for repo in repositories:
        if repo.get("isFork"):
            continue
        for edge in repo.get("languages", {}).get("edges", []):
            name = edge.get("node", {}).get("name")
            size = int(edge.get("size") or 0)
            if name and size > 0:
                sizes[name] += size

    if not sizes:
        return "No language data"

    total = sum(sizes.values())
    top = sizes.most_common(3)
    parts = [f"{name} {round(size / total * 100)}%" for name, size in top]
    return ", ".join(parts)


def make_sparkline(calendar: dict) -> str:
    day_counts = {}
    for week in calendar.get("weeks", []):
        for day in week.get("contributionDays", []):
            day_counts[day["date"]] = int(day["contributionCount"])

    today = datetime.now(timezone.utc).date()
    start = today - timedelta(days=363)

    values = []
    current = start
    while current <= today:
        week_total = 0
        for _ in range(7):
            if current > today:
                break
            week_total += day_counts.get(current.isoformat(), 0)
            current += timedelta(days=1)
        values.append(week_total)

    values = values[-52:]
    maximum = max(values, default=0)
    levels = "▁▂▃▄▅▆▇█"
    if maximum == 0:
        return " " * 52

    chars = []
    for value in values:
        if value == 0:
            chars.append(" ")
            continue
        index = min(7, max(0, round(value / maximum * 7)))
        chars.append(levels[index])

    return "".join(chars).ljust(52)


def replace_value(svg: str, label: str, value_color: str, value: str) -> str:
    escaped = html.escape(str(value), quote=False)
    pattern = re.compile(
        rf'({re.escape(label)}.*?<tspan fill="{re.escape(value_color)}"> )([^<]*)(</tspan>)'
    )
    updated, count = pattern.subn(rf"\g<1>{escaped}\g<3>", svg, count=1)
    if count != 1:
        raise RuntimeError(f"Could not find SVG field: {label}")
    return updated


def replace_sparkline(svg: str, color: str, sparkline: str) -> str:
    pattern = re.compile(rf'(<tspan fill="{re.escape(color)}">)(.*?)(</tspan>)')
    updated, count = pattern.subn(
        lambda m: f"{m.group(1)}{html.escape(sparkline, quote=False)}{m.group(3)}",
        svg,
        count=1,
    )
    if count != 1:
        raise RuntimeError("Could not find SVG contribution sparkline")
    return updated


def update_svg(path: Path, stats: dict, theme: str) -> None:
    svg = path.read_text(encoding="utf-8")

    if theme == "dark":
        value = {
            "uptime": "#c9d1d9",
            "languages": "#c9d1d9",
            "repos": "#79c0ff",
            "stars": "#79c0ff",
            "forks": "#79c0ff",
            "followers": "#79c0ff",
            "commits": "#79c0ff",
            "contributed": "#79c0ff",
            "prs": "#79c0ff",
            "issues": "#79c0ff",
            "top_repo": "#c9d1d9",
            "contributions": "#79c0ff",
            "reviews": "#79c0ff",
            "private": "#79c0ff",
            "sparkline": "#39d353",
        }
    else:
        value = {
            "uptime": "#24292f",
            "languages": "#24292f",
            "repos": "#0550ae",
            "stars": "#0550ae",
            "forks": "#0550ae",
            "followers": "#0550ae",
            "commits": "#0550ae",
            "contributed": "#0550ae",
            "prs": "#0550ae",
            "issues": "#0550ae",
            "top_repo": "#24292f",
            "contributions": "#0550ae",
            "reviews": "#0550ae",
            "private": "#0550ae",
            "sparkline": "#2da44e",
        }

    fields = [
        (". Uptime:", "uptime"),
        (". Languages:", "languages"),
        (". Repos:", "repos"),
        (". Stars:", "stars"),
        (". Forks:", "forks"),
        (". Followers:", "followers"),
        (". Commits:", "commits"),
        (". Contributed:", "contributed"),
        (". PRs:", "prs"),
        (". Issues:", "issues"),
        (". Top repo:", "top_repo"),
        (". Contributions:", "contributions"),
        (". Reviews:", "reviews"),
        (". Private:", "private"),
    ]

    for label, key in fields:
        svg = replace_value(svg, label, value[key], stats[key])

    svg = replace_sparkline(svg, value["sparkline"], stats["sparkline"])
    path.write_text(svg, encoding="utf-8")


def main() -> int:
    now = datetime.now(timezone.utc)
    from_time = now - timedelta(days=365)

    data = graphql(
        QUERY,
        {
            "login": USERNAME,
            "from": from_time.isoformat().replace("+00:00", "Z"),
            "to": now.isoformat().replace("+00:00", "Z"),
        },
    )

    user = data["user"]
    repos = user["repositories"]["nodes"]
    collection = user["contributionsCollection"]

    stats = {
        "uptime": format_uptime(user["createdAt"], now),
        "languages": format_languages(repos),
        "repos": user["repositories"]["totalCount"],
        "stars": sum(int(repo.get("stargazerCount") or 0) for repo in repos),
        "forks": sum(int(repo.get("forkCount") or 0) for repo in repos),
        "followers": user["followers"]["totalCount"],
        # All-time authored counts from GitHub Search.
        "commits": search_count(
            f"author:{USERNAME}",
            "https://api.github.com/search/commits",
        ),
        # Number of repositories this account committed to in the last 12 months.
        "contributed": collection["totalRepositoriesWithContributedCommits"],
        # All-time authored PR/issue counts.
        "prs": search_count(f"author:{USERNAME} is:pr"),
        "issues": search_count(f"author:{USERNAME} is:issue"),
        "top_repo": "No public repositories",
        "contributions": collection["totalContributions"],
        "reviews": collection["totalPullRequestReviewContributions"],
        # Private contribution counts are available when the token has the
        # appropriate user scope and private contribution sharing is enabled.
        "private": collection["restrictedContributionsCount"],
        "sparkline": make_sparkline(collection["contributionCalendar"]),
    }

    if repos:
        top_repo = max(
            repos,
            key=lambda repo: (
                int(repo.get("stargazerCount") or 0),
                repo.get("nameWithOwner", ""),
            ),
        )
        stats["top_repo"] = (
            f"{top_repo['name']} ({int(top_repo.get('stargazerCount') or 0)} ★)"
        )

    for theme, path in FILES.items():
        update_svg(path, stats, theme)

    print(json.dumps(stats, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise
