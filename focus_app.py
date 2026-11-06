#!/usr/bin/env python3
"""
Focus Saver - Native macOS Menu Bar Application
Menü çubuğundan tek tıkla hem Safari'de hem Chrome'da dikkat dağıtıcı siteleri kilitler.
"""

import os
import subprocess
import sys

# Proje dizinini sys.path'e ekle
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import rumps
from core.session_manager import FocusSessionManager


class FocusSaverApp(rumps.App):
    def __init__(self):
        super().__init__("Focus Saver", title="🎯 Focus")
        self.session_mgr = FocusSessionManager()

        # Menü öğeleri
        self.item_25 = rumps.MenuItem("⚡ 25 dk (Pomodoro)", callback=lambda _: self.start_session(25))
        self.item_45 = rumps.MenuItem("⚡ 45 dk (Derin Odak)", callback=lambda _: self.start_session(45))
        self.item_60 = rumps.MenuItem("⚡ 60 dk", callback=lambda _: self.start_session(60))
        self.item_15 = rumps.MenuItem("⚡ 15 dk (Hızlı Odak)", callback=lambda _: self.start_session(15))
        self.item_custom = rumps.MenuItem("✍️ Özel Süre Belirle...", callback=self.custom_duration)

        self.item_stop = rumps.MenuItem("⏹️ Seansı Durdur / Vazgeç", callback=self.stop_session)
        self.item_status = rumps.MenuItem("🛡️ Durum: Hazır")
        self.item_blocked = rumps.MenuItem("🚫 Engelli: YouTube, Kick, Twitch, IG")
        self.item_allowed = rumps.MenuItem("🎵 Serbest: YouTube Music")
        self.item_quit = rumps.MenuItem("🚪 Çıkış", callback=self.quit_app)

        self.menu = [
            self.item_25,
            self.item_45,
            self.item_60,
            self.item_15,
            self.item_custom,
            None,
            self.item_stop,
            None,
            self.item_status,
            self.item_blocked,
            self.item_allowed,
            None,
            self.item_quit,
        ]

        # 1 saniyelik periyodik sayaç
        self.timer = rumps.Timer(self.on_tick, 1)
        self.timer.start()

    def _show_alert(self, title, message):
        """macOS yerel uyarı penceresi gösterir"""
        try:
            script = f'tell application "System Events" to display alert "{title}" message "{message}"'
            subprocess.run(["osascript", "-e", script], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except Exception:
            pass

    def start_session(self, minutes):
        self.session_mgr.start(minutes)
        self.title = f"🎯 {minutes:02d}:00"
        self.item_status.title = f"🛡️ KORUMA AKTİF ({minutes} dk)"

    def custom_duration(self, _):
        script = '''
        tell application "System Events"
            activate
            try
                set dialogResult to display dialog "Kaç dakika odaklanmak istiyorsunuz?" default answer "30" with title "Focus Saver - Özel Odak Süresi" buttons {"İptal", "Başlat"} default button "Başlat"
                return text returned of dialogResult
            on error number -128
                return "CANCEL"
            end try
        end tell
        '''
        try:
            res = subprocess.check_output(["osascript", "-e", script], text=True).strip()
            if res == "CANCEL" or not res:
                return

            mins = int(res)
            if mins > 0:
                self.start_session(mins)
            else:
                self._show_alert("Geçersiz Süre", "Lütfen 0'dan büyük bir dakika girin.")
        except ValueError:
            self._show_alert("Hata", "Lütfen sadece geçerli bir sayı girin (örnek: 30).")
        except Exception as e:
            print(f"[Focus Saver] Özel süre belirleme hatası: {e}")

    def stop_session(self, _):
        if self.session_mgr.is_running:
            self.session_mgr.stop()
            self.title = "🎯 Focus"
            self.item_status.title = "🛡️ Durum: Hazır"
        else:
            self._show_alert("Bilgi", "Zaten aktif bir odak seansı bulunmuyor.")

    def on_tick(self, _):
        if self.session_mgr.is_running:
            rem = self.session_mgr.get_remaining_seconds()
            if rem > 0:
                self.title = f"🎯 {self.session_mgr.get_formatted_time()}"
                self.item_status.title = f"🛡️ KORUMA AKTİF ({self.session_mgr.get_formatted_time()})"
            else:
                self.title = "🎯 Focus"
                self.item_status.title = "🛡️ Durum: Hazır"
        else:
            if self.title != "🎯 Focus":
                self.title = "🎯 Focus"
                self.item_status.title = "🛡️ Durum: Hazır"

    def quit_app(self, _):
        self.session_mgr.stop()
        rumps.quit_application()


if __name__ == "__main__":
    app = FocusSaverApp()
    app.run()
