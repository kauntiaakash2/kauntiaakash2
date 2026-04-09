const app = document.getElementById("app");
const bootScreen = document.getElementById("boot-screen");
const bootStatus = document.getElementById("boot-status");
const progressBar = document.getElementById("progress-bar");

const matrixCanvas = document.getElementById("matrix");
const matrixCtx = matrixCanvas.getContext("2d");

function resizeMatrix() {
  matrixCanvas.width = window.innerWidth;
  matrixCanvas.height = window.innerHeight;
}

const glyphs = "01アイウエオカキクケコサシスセソABCDEFGHIJKLMNOPQRSTUVWXYZ";
let columns = [];

function initColumns() {
  const colCount = Math.floor(matrixCanvas.width / 18);
  columns = Array.from({ length: colCount }, () => Math.floor(Math.random() * -40));
}

function drawMatrix() {
  matrixCtx.fillStyle = "rgba(0, 0, 0, 0.08)";
  matrixCtx.fillRect(0, 0, matrixCanvas.width, matrixCanvas.height);

  matrixCtx.fillStyle = "#75fa97";
  matrixCtx.font = "16px 'Share Tech Mono', monospace";

  columns.forEach((y, i) => {
    const text = glyphs[Math.floor(Math.random() * glyphs.length)];
    const x = i * 18;
    matrixCtx.fillText(text, x, y * 18);
    columns[i] = y > matrixCanvas.height / 18 && Math.random() > 0.975 ? 0 : y + 1;
  });
}

resizeMatrix();
initColumns();
window.addEventListener("resize", () => {
  resizeMatrix();
  initColumns();
});

let bootProgress = 0;
const bootSteps = [
  "Loading neural modules...",
  "Syncing telemetry...",
  "Compiling portfolio kernels...",
  "Launching interface layers...",
  "Finalizing visual systems...",
];

const bootInterval = setInterval(() => {
  bootProgress += Math.floor(Math.random() * 9) + 4;
  if (bootProgress > 100) bootProgress = 100;

  const status = bootSteps[Math.min(bootSteps.length - 1, Math.floor(bootProgress / 22))];
  bootStatus.textContent = `[${String(bootProgress).padStart(2, "0")}%] ${status}`;
  progressBar.style.width = `${bootProgress}%`;

  if (bootProgress === 100) {
    clearInterval(bootInterval);
    setTimeout(() => {
      bootScreen.classList.add("fade-out");
      app.classList.remove("hidden");
      app.style.pointerEvents = "auto";
      startMainAnimations();
    }, 650);
  }
}, 240);

const matrixLoop = setInterval(drawMatrix, 45);
setTimeout(() => clearInterval(matrixLoop), 6500);

const starCanvas = document.getElementById("starfield");
const starCtx = starCanvas.getContext("2d");
let stars = [];
let starsActive = false;

function resizeStars() {
  starCanvas.width = window.innerWidth;
  starCanvas.height = window.innerHeight;
  const count = Math.max(90, Math.floor((starCanvas.width * starCanvas.height) / 9000));
  stars = Array.from({ length: count }, () => ({
    x: Math.random() * starCanvas.width,
    y: Math.random() * starCanvas.height,
    r: Math.random() * 1.8 + 0.2,
    vx: (Math.random() - 0.5) * 0.18,
    vy: (Math.random() - 0.5) * 0.18,
    a: Math.random() * 0.7 + 0.2,
  }));
}

function drawStars() {
  if (!starsActive) return;
  starCtx.clearRect(0, 0, starCanvas.width, starCanvas.height);

  for (const s of stars) {
    s.x += s.vx;
    s.y += s.vy;

    if (s.x < 0) s.x = starCanvas.width;
    if (s.x > starCanvas.width) s.x = 0;
    if (s.y < 0) s.y = starCanvas.height;
    if (s.y > starCanvas.height) s.y = 0;

    starCtx.beginPath();
    starCtx.arc(s.x, s.y, s.r, 0, Math.PI * 2);
    starCtx.fillStyle = `rgba(160, 245, 255, ${s.a})`;
    starCtx.fill();
  }

  requestAnimationFrame(drawStars);
}

function startMainAnimations() {
  starsActive = true;
  resizeStars();
  drawStars();

  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) entry.target.classList.add("show");
      });
    },
    { threshold: 0.18 },
  );

  document.querySelectorAll(".reveal").forEach((el) => observer.observe(el));
}

window.addEventListener("resize", resizeStars);
