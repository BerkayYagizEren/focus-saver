"""
Focus Saver - Session Manager
Zamanlayıcıyı, NetworkManager (PAC Proxy) ve TabWatcher motorlarını tek merkezden yönetir.
"""

import atexit
import subprocess
import time
from .network_manager import NetworkManager
from .tab_watcher import TabWatcher


class FocusSessionManager:
    def __init__(self):
        self.network_mgr = NetworkManager()
        self.tab_watcher = TabWatcher(check_interval=0.7)

        self.is_running = False
        self.duration_minutes = 25
        self.start_time = None
        self.end_time = None

        # Güvenlik önlemi
        atexit.register(self.stop)

    def send_notification(self, title, message, sound="Glass"):
        try:
            cmd = f'display notification "{message}" with title "{title}" sound name "{sound}"'
            subprocess.run(["osascript", "-e", cmd], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except Exception:
            pass

    def start(self, duration_minutes=25):
        if self.is_running:
            self.stop()

        self.duration_minutes = duration_minutes
        self.start_time = time.time()
        self.end_time = self.start_time + (duration_minutes * 60)
        self.is_running = True

        # 1. PAC Proxy'yi devreye al (Ağ seviyesinde kesinti)
        self.network_mgr.enable_protection()

        # 2. Safari & Chrome sekme izleyicisini başlat
        self.tab_watcher.start()

        # 3. macOS Bildirimi gönder
        self.send_notification(
            "Focus Saver Başladı 🎯",
            f"{duration_minutes} dakikalık odak seansı devrede. YouTube Music serbest!"
        )

    def stop(self, completed=False):
        if not self.is_running and not self.network_mgr.is_active:
            return

        self.is_running = False
        self.start_time = None
        self.end_time = None

        # Korumaları kaldır
        self.tab_watcher.stop()
        self.network_mgr.disable_protection()

        if completed:
            self.send_notification(
                "Tebrikler! 🎉",
                "Odaklanma süreniz tamamlandı. Tüm sitelere erişim serbest.",
                sound="Hero"
            )
        else:
            self.send_notification(
                "Focus Saver Durduruldu",
                "Odak seansı sonlandırıldı, korumalar kaldırıldı."
            )

    def get_remaining_seconds(self):
        if not self.is_running or not self.end_time:
            return 0
        rem = int(self.end_time - time.time())
        if rem <= 0:
            self.stop(completed=True)
            return 0
        return rem

    def get_formatted_time(self):
        rem = self.get_remaining_seconds()
        mins = rem // 60
        secs = rem % 60
        return f"{mins:02d}:{secs:02d}"
