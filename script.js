const canvas = document.getElementById("starfield");
const ctx = canvas.getContext("2d");

let stars = [];

function resize() {
  canvas.width = window.innerWidth;
  canvas.height = window.innerHeight;
  const count = Math.max(90, Math.floor((canvas.width * canvas.height) / 9000));
  stars = Array.from({ length: count }, () => ({
    x: Math.random() * canvas.width,
    y: Math.random() * canvas.height,
    r: Math.random() * 1.8 + 0.2,
    vx: (Math.random() - 0.5) * 0.18,
    vy: (Math.random() - 0.5) * 0.18,
    a: Math.random() * 0.7 + 0.2,
  }));
}

function draw() {
  ctx.clearRect(0, 0, canvas.width, canvas.height);
  for (const s of stars) {
    s.x += s.vx;
    s.y += s.vy;

    if (s.x < 0) s.x = canvas.width;
    if (s.x > canvas.width) s.x = 0;
    if (s.y < 0) s.y = canvas.height;
    if (s.y > canvas.height) s.y = 0;

    ctx.beginPath();
    ctx.arc(s.x, s.y, s.r, 0, Math.PI * 2);
    ctx.fillStyle = `rgba(160, 245, 255, ${s.a})`;
    ctx.fill();
  }
  requestAnimationFrame(draw);
}

const observer = new IntersectionObserver(
  (entries) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        entry.target.classList.add("show");
      }
    });
  },
  { threshold: 0.18 },
);

document.querySelectorAll(".reveal").forEach((el) => observer.observe(el));

window.addEventListener("resize", resize);
resize();
draw();
