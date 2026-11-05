#!/usr/bin/env python3
"""
Focus Saver - Native macOS Menu Bar Application
Menü çubuğundan tek tıkla hem Safari'de hem Chrome'da dikkat dağıtıcı siteleri kilitler.
"""

import os
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

    def start_session(self, minutes):
        self.session_mgr.start(minutes)
        self.title = f"🎯 {minutes:02d}:00"
        self.item_status.title = f"🛡️ KORUMA AKTİF ({minutes} dk)"
        rumps.notification(
            title="Focus Saver",
            subtitle=f"{minutes} dakikalık odak süresi başladı",
            message="Safari ve Chrome korumaya alındı. YouTube Music serbest!"
        )

    def custom_duration(self, _):
        window = rumps.Window(
            message="Kaç dakika odaklanmak istiyorsunuz?",
            title="Özel Odak Süresi",
            default_text="30",
            ok="Başlat",
            cancel="İptal",
            dimensions=(220, 24)
        )
        response = window.run()
        if response.clicked:
            try:
                mins = int(response.text.strip())
                if mins > 0:
                    self.start_session(mins)
            except ValueError:
                rumps.alert("Hata", "Lütfen geçerli bir sayı girin.")

    def stop_session(self, _):
        if self.session_mgr.is_running:
            self.session_mgr.stop()
            self.title = "🎯 Focus"
            self.item_status.title = "🛡️ Durum: Hazır"
            rumps.notification(
                title="Focus Saver",
                subtitle="Seans durduruldu",
                message="Korumalar kaldırıldı, tüm sitelere erişim serbest."
            )
        else:
            rumps.alert("Bilgi", "Zaten aktif bir odak seansı bulunmuyor.")

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
