// Focus Saver - Popup Script
const timeText = document.getElementById("timeText");
const timeSubtext = document.getElementById("timeSubtext");
const statusPill = document.getElementById("statusPill");
const toggleBtn = document.getElementById("toggleBtn");
const toggleBtnText = document.getElementById("toggleBtnText");
const setupControls = document.getElementById("setupControls");
const progressCircle = document.getElementById("progressCircle");
const customMinutesInput = document.getElementById("customMinutes");
const presetButtons = document.querySelectorAll(".preset-btn");

const RADIUS = 70;
const CIRCUMFERENCE = 2 * Math.PI * RADIUS;

// Progress circle setup
progressCircle.style.strokeDasharray = `${CIRCUMFERENCE} ${CIRCUMFERENCE}`;
progressCircle.style.strokeDashoffset = "0";

let selectedMinutes = 25;
let timerInterval = null;
let currentSessionEndTime = null;
let currentSessionTotalSeconds = 25 * 60;

// Sayfa açıldığında durumu sorgula
document.addEventListener("DOMContentLoaded", async () => {
  setupEventListeners();
  await refreshUI();
});

// Event Listener tanımlamaları
function setupEventListeners() {
  presetButtons.forEach((btn) => {
    btn.addEventListener("click", () => {
      presetButtons.forEach((b) => b.classList.remove("active"));
      btn.classList.add("active");
      selectedMinutes = parseInt(btn.dataset.min, 10);
      customMinutesInput.value = selectedMinutes;
      updateDisplayTime(selectedMinutes * 60);
    });
  });

  customMinutesInput.addEventListener("input", (e) => {
    const val = parseInt(e.target.value, 10);
    if (!isNaN(val) && val > 0) {
      selectedMinutes = Math.min(300, Math.max(1, val));
      presetButtons.forEach((b) => {
        b.classList.toggle("active", parseInt(b.dataset.min, 10) === selectedMinutes);
      });
      updateDisplayTime(selectedMinutes * 60);
    }
  });

  toggleBtn.addEventListener("click", async () => {
    const isRunning = toggleBtn.classList.contains("stop");

    if (!isRunning) {
      // Başlat
      const duration = selectedMinutes;
      const response = await chrome.runtime.sendMessage({
        type: "START_TIMER",
        durationMinutes: duration
      });

      if (response && response.success) {
        await refreshUI();
      }
    } else {
      // Durdur
      const response = await chrome.runtime.sendMessage({
        type: "STOP_TIMER"
      });

      if (response && response.success) {
        await refreshUI();
      }
    }
  });
}

// Background'dan güncel durumu alıp UI'ı senkronize eder
async function refreshUI() {
  const state = await chrome.runtime.sendMessage({ type: "GET_STATUS" });

  if (state.timerStatus === "running" && state.endTime && state.remainingSeconds > 0) {
    currentSessionEndTime = state.endTime;
    currentSessionTotalSeconds = state.durationMinutes * 60;
    renderRunningState(state.remainingSeconds);
    startLocalTicker();
  } else {
    stopLocalTicker();
    renderIdleState();
  }
}

function renderRunningState(remainingSeconds) {
  statusPill.textContent = "KORUMA AKTİF";
  statusPill.className = "status-pill active";

  timeSubtext.textContent = "Kalan Süre";
  progressCircle.style.stroke = "#ef4444";

  setupControls.style.opacity = "0.3";
  setupControls.style.pointerEvents = "none";

  toggleBtn.className = "action-btn stop";
  toggleBtnText.textContent = "Seansı Durdur / Vazgeç";

  updateDisplayTime(remainingSeconds);
  updateProgressRing(remainingSeconds, currentSessionTotalSeconds);
}

function renderIdleState() {
  statusPill.textContent = "Hazır";
  statusPill.className = "status-pill idle";

  timeSubtext.textContent = "Odak Süresi";
  progressCircle.style.stroke = "#6366f1";

  setupControls.style.opacity = "1";
  setupControls.style.pointerEvents = "auto";

  toggleBtn.className = "action-btn start";
  toggleBtnText.textContent = "Odaklanmayı Başlat";

  updateDisplayTime(selectedMinutes * 60);
  setProgress(1); // Tam çember
}

function startLocalTicker() {
  if (timerInterval) clearInterval(timerInterval);

  timerInterval = setInterval(() => {
    if (!currentSessionEndTime) return;

    const remaining = Math.max(0, Math.floor((currentSessionEndTime - Date.now()) / 1000));

    if (remaining <= 0) {
      stopLocalTicker();
      renderIdleState();
    } else {
      updateDisplayTime(remaining);
      updateProgressRing(remaining, currentSessionTotalSeconds);
    }
  }, 1000);
}

function stopLocalTicker() {
  if (timerInterval) {
    clearInterval(timerInterval);
    timerInterval = null;
  }
}

function updateDisplayTime(totalSeconds) {
  const minutes = Math.floor(totalSeconds / 60);
  const seconds = totalSeconds % 60;
  timeText.textContent = `${String(minutes).padStart(2, "0")}:${String(seconds).padStart(2, "0")}`;
}

function updateProgressRing(remainingSeconds, totalSeconds) {
  const ratio = Math.max(0, Math.min(1, remainingSeconds / totalSeconds));
  setProgress(ratio);
}

function setProgress(ratio) {
  const offset = CIRCUMFERENCE - ratio * CIRCUMFERENCE;
  progressCircle.style.strokeDashoffset = offset;
}
