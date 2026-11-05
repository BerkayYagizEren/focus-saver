"""
Focus Saver - Tab Watcher
Safari ve Google Chrome sekmelerini anlık olarak izler.
- music.youtube.com'u kesinlikle serbest bırakır.
- youtube.com, youtu.be, kick.com, twitch.tv, instagram.com sekmelerini anında kapatır.
- Google / Safari / Bing / DuckDuckGo üzerinden yapılan odak kırıcı arama sorgularını anında kapatır.
"""

import subprocess
import threading
import time
import urllib.parse

BLOCKED_DOMAINS = [
    "youtube.com",
    "youtu.be",
    "kick.com",
    "twitch.tv",
    "instagram.com",
]

BLOCKED_KEYWORDS = ["youtube", "kick", "twitch", "instagram"]

INSPECT_APPLESCRIPT = """
set res to ""
tell application "System Events"
    set isSafariRunning to (name of processes) contains "Safari"
    set isChromeRunning to (name of processes) contains "Google Chrome"
end tell

if isSafariRunning then
    tell application "Safari"
        repeat with wIdx from 1 to count of windows
            set w to window wIdx
            repeat with tIdx from 1 to count of tabs of w
                set t to tab tIdx of w
                set u to (URL of t) as text
                set res to res & "SAFARI|" & wIdx & "|" & tIdx & "|" & u & linefeed
            end repeat
        end repeat
    end tell
end if

if isChromeRunning then
    tell application "Google Chrome"
        repeat with wIdx from 1 to count of windows
            set w to window wIdx
            repeat with tIdx from 1 to count of tabs of w
                set t to tab tIdx of w
                set u to (URL of t) as text
                set res to res & "CHROME|" & wIdx & "|" & tIdx & "|" & u & linefeed
            end repeat
        end repeat
    end tell
end if

return res
"""


class TabWatcher:
    def __init__(self, check_interval=0.6):
        self.check_interval = check_interval
        self._running = False
        self._thread = None

    def is_violating_url(self, raw_url):
        """URL'nin yasaklı bir platform veya arama olup olmadığını denetler"""
        if not raw_url or raw_url.startswith("chrome://") or raw_url.startswith("about:"):
            return False

        try:
            parsed = urllib.parse.urlparse(raw_url)
            host = (parsed.hostname or "").lower()

            # 1. KRİTİK İSTİSNA: YouTube Music her zaman serbest
            if host == "music.youtube.com" or host.endswith(".music.youtube.com"):
                return False

            # 2. Doğrudan domain engeli
            for d in BLOCKED_DOMAINS:
                if host == d or host.endswith("." + d):
                    return True

            # 3. Arama Motoru Sorgu Denetimi (Google, Safari Default, Bing, DuckDuckGo, Yandex)
            is_search_engine = any(
                engine in host
                for engine in ["google.", "duckduckgo.", "bing.", "yandex.", "ecosia."]
            )
            if is_search_engine:
                query_params = urllib.parse.parse_qs(parsed.query)
                query_values = []
                for param in ["q", "query", "p", "text"]:
                    if param in query_params:
                        query_values.extend(query_params[param])

                combined_query = " ".join(query_values).lower()
                for keyword in BLOCKED_KEYWORDS:
                    if keyword in combined_query:
                        return True

        except Exception:
            pass

        return False

    def close_violating_tab(self, browser, w_idx, t_idx, url):
        """Yasaklı sekmeyi anında kapatır"""
        try:
            if browser == "SAFARI":
                cmd = f'tell application "Safari" to close tab {t_idx} of window {w_idx}'
            elif browser == "CHROME":
                cmd = f'tell application "Google Chrome" to close tab {t_idx} of window {w_idx}'
            else:
                return

            subprocess.run(
                ["osascript", "-e", cmd],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            print(f"[TabWatcher] {browser} üzerindeki odak kırıcı sekme kapatıldı: {url[:50]}...")
        except Exception as e:
            print(f"[TabWatcher] Sekme kapatılırken hata: {e}")

    def scan_and_enforce(self):
        """Açık sekmeleri tarar ve kural ihlallerini düşürür"""
        try:
            output = subprocess.check_output(
                ["osascript", "-e", INSPECT_APPLESCRIPT], text=True
            ).strip()

            if not output:
                return

            # Sekmeleri tersten kapatmak indeks kaymasını önler
            lines = output.splitlines()
            for line in reversed(lines):
                parts = line.strip().split("|", 3)
                if len(parts) == 4:
                    browser, w_idx, t_idx, url = parts
                    if self.is_violating_url(url):
                        self.close_violating_tab(browser, w_idx, t_idx, url)
        except Exception:
            pass

    def _loop(self):
        while self._running:
            self.scan_and_enforce()
            time.sleep(self.check_interval)

    def start(self):
        if self._running:
            return
        self._running = True
        # İlk anda hemen tara
        self.scan_and_enforce()
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()
        print("[TabWatcher] Safari ve Chrome tarayıcı izleme motoru başlatıldı.")

    def stop(self):
        self._running = False
        if self._thread:
            self._thread.join(timeout=1.0)
            self._thread = None
        print("[TabWatcher] Tarayıcı izleme motoru durduruldu.")
