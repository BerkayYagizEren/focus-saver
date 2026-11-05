// Focus Saver - Background Service Worker (Manifest V3)
// Chrome & Safari WebExtension Uyumlu

const RULESET_ID = "focus_ruleset";
const BLOCKED_DOMAINS = ["youtube.com", "youtu.be", "kick.com", "twitch.tv", "instagram.com"];

// Başlangıç durum kontrolü
chrome.runtime.onInstalled.addListener(async () => {
  console.log("[Focus Saver] Extension yüklendi.");
  const data = await chrome.storage.local.get(["timerStatus"]);
  if (!data.timerStatus || data.timerStatus === "idle") {
    await setProtectionEnabled(false);
    await updateBadge("");
  } else if (data.timerStatus === "running") {
    // Tarayıcı yeniden başlatıldıysa süreyi kontrol et
    await checkTimerStatus();
  }
});

// Alarm tetiklendiğinde
chrome.alarms.onAlarm.addListener(async (alarm) => {
  if (alarm.name === "focusTimerAlarm") {
    await finishFocusSession();
  } else if (alarm.name === "focusBadgeUpdate") {
    await updateBadgeTimer();
  }
});

// Mesaj dinleyici (Popup -> Background)
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.type === "START_TIMER") {
    startFocusSession(message.durationMinutes)
      .then(() => sendResponse({ success: true }))
      .catch((err) => sendResponse({ success: false, error: err.message }));
    return true; // async yanıt için
  }

  if (message.type === "STOP_TIMER") {
    stopFocusSession()
      .then(() => sendResponse({ success: true }))
      .catch((err) => sendResponse({ success: false, error: err.message }));
    return true;
  }

  if (message.type === "GET_STATUS") {
    getTimerState().then((state) => sendResponse(state));
    return true;
  }
});

/**
 * Odaklanma seansını başlatır
 */
async function startFocusSession(durationMinutes) {
  const durationMs = durationMinutes * 60 * 1000;
  const startTime = Date.now();
  const endTime = startTime + durationMs;

  const state = {
    timerStatus: "running",
    durationMinutes: durationMinutes,
    startTime: startTime,
    endTime: endTime
  };

  await chrome.storage.local.set(state);

  // 1. Kuralları aktif et (Bağlantı kırma motoru)
  await setProtectionEnabled(true);

  // 2. Halihazırda açık olan dikkat dağıtıcı sekmelerin bağlantısını anında kes
  await dropExistingBlockedTabs();

  // 3. Alarmları kur
  await chrome.alarms.clearAll();
  chrome.alarms.create("focusTimerAlarm", { when: endTime });
  chrome.alarms.create("focusBadgeUpdate", { periodInMinutes: 1 });

  // 4. Badge'i güncelle
  await updateBadge(`${durationMinutes}m`);

  console.log(`[Focus Saver] ${durationMinutes} dakikalık seans başladı.`);
}

/**
 * Odaklanma seansını kullanıcı isteğiyle durdurur
 */
async function stopFocusSession() {
  await chrome.alarms.clearAll();
  await setProtectionEnabled(false);

  await chrome.storage.local.set({
    timerStatus: "idle",
    startTime: null,
    endTime: null
  });

  await updateBadge("");
  console.log("[Focus Saver] Seans durduruldu, koruma kaldırıldı.");
}

/**
 * Süre dolduğunda seansı başarıyla tamamlar
 */
async function finishFocusSession() {
  await stopFocusSession();

  // Bildirim gönder
  if (chrome.notifications) {
    chrome.notifications.create({
      type: "basic",
      iconUrl: "icons/icon128.png",
      title: "Focus Saver",
      message: "Tebrikler! Odaklanma süreniz tamamlandı. Korumalar kaldırıldı.",
      priority: 2
    });
  }
}

/**
 * DeclarativeNetRequest kurallarını açar / kapatır
 */
async function setProtectionEnabled(enable) {
  try {
    if (enable) {
      await chrome.declarativeNetRequest.updateEnabledRulesets({
        enableRulesetIds: [RULESET_ID]
      });
      console.log("[Focus Saver] declarativeNetRequest kuralları AKTİF.");
    } else {
      await chrome.declarativeNetRequest.updateEnabledRulesets({
        disableRulesetIds: [RULESET_ID]
      });
      console.log("[Focus Saver] declarativeNetRequest kuralları DEVRE DIŞI.");
    }
  } catch (err) {
    console.error("[Focus Saver] Ruleset güncelleme hatası:", err);
  }
}

/**
 * Açık olan yasaklı sekmeleri yenileyerek bağlantılarını derhal keser (music.youtube.com hariç)
 */
async function dropExistingBlockedTabs() {
  try {
    const tabs = await chrome.tabs.query({});
    for (const tab of tabs) {
      if (!tab.url) continue;

      try {
        const url = new URL(tab.url);

        // music.youtube.com kesinlikle serbest
        if (url.hostname === "music.youtube.com") {
          continue;
        }

        const isBlocked = BLOCKED_DOMAINS.some((domain) =>
          url.hostname === domain || url.hostname.endsWith("." + domain)
        );

        if (isBlocked) {
          // Sekmeyi yeniden yükle; kural aktif olduğu için doğrudan ağ bağlantısı kopacak
          chrome.tabs.reload(tab.id);
        }
      } catch (e) {
        // Geçersiz URL'leri atla (örn: chrome://)
      }
    }
  } catch (err) {
    console.warn("[Focus Saver] Sekmeleri tararken hata:", err);
  }
}

/**
 * Rozet (badge) üzerindeki kalan dakikayı günceller
 */
async function updateBadgeTimer() {
  const state = await getTimerState();
  if (state.timerStatus !== "running" || !state.endTime) {
    await updateBadge("");
    return;
  }

  const remainingMs = state.endTime - Date.now();
  if (remainingMs <= 0) {
    await finishFocusSession();
    return;
  }

  const remainingMins = Math.ceil(remainingMs / 60000);
  await updateBadge(`${remainingMins}m`);
}

async function updateBadge(text) {
  try {
    await chrome.action.setBadgeText({ text: text });
    await chrome.action.setBadgeBackgroundColor({ color: "#EF4444" }); // Odak kırmızısı
  } catch (err) {
    // Bazı ortamlarda sessizce geç
  }
}

async function checkTimerStatus() {
  const state = await getTimerState();
  if (state.timerStatus === "running" && state.endTime) {
    if (Date.now() >= state.endTime) {
      await finishFocusSession();
    } else {
      await setProtectionEnabled(true);
      await updateBadgeTimer();
    }
  } else {
    await setProtectionEnabled(false);
    await updateBadge("");
  }
}

async function getTimerState() {
  const data = await chrome.storage.local.get([
    "timerStatus",
    "durationMinutes",
    "startTime",
    "endTime"
  ]);
  return {
    timerStatus: data.timerStatus || "idle",
    durationMinutes: data.durationMinutes || 25,
    startTime: data.startTime || null,
    endTime: data.endTime || null,
    remainingSeconds: data.endTime ? Math.max(0, Math.floor((data.endTime - Date.now()) / 1000)) : 0
  };
}
