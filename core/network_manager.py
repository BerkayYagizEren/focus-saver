"""
Focus Saver - Network Manager (macOS PAC Proxy Engine)
Tüm macOS tarayıcılarında (Safari, Chrome, Brave, Arc vb.)
ağ seviyesinde doğrudan bağlantı kesilmesini sağlar.
"""

import atexit
import http.server
import os
import signal
import socketserver
import subprocess
import threading
import time

PAC_PORT = 8765
PAC_URL = f"http://127.0.0.1:{PAC_PORT}/proxy.pac"

PAC_TEMPLATE = """// Focus Saver Auto-Proxy Configuration
function FindProxyForURL(url, host) {
    // 1. YouTube Music KESİNLİKLE SERBEST
    if (host === "music.youtube.com" || host.endsWith(".music.youtube.com")) {
        return "DIRECT";
    }

    // 2. Yasaklı platformlar - Port 9'a yönlendirerek doğrudan bağlantıyı kopar
    var blocked = [
        "youtube.com",
        "youtu.be",
        "kick.com",
        "twitch.tv",
        "instagram.com"
    ];

    for (var i = 0; i < blocked.length; i++) {
        var domain = blocked[i];
        if (host === domain || dnsDomainIs(host, "." + domain)) {
            return "PROXY 127.0.0.1:9";
        }
    }

    // 3. Diğer tüm bağlantılar doğrudan serbest
    return "DIRECT";
}
"""


class PacHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path in ["/proxy.pac", "/"]:
            data = PAC_TEMPLATE.encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/x-ns-proxy-autoconfig")
            self.send_header("Content-Length", str(len(data)))
            self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
            self.end_headers()
            self.wfile.write(data)
        else:
            self.send_error(404)

    def log_message(self, format, *args):
        # Sessiz mod (konsolu kirletme)
        return


class NetworkManager:
    def __init__(self, port=PAC_PORT):
        self.port = port
        self.pac_url = f"http://127.0.0.1:{self.port}/proxy.pac"
        self.server = None
        self.server_thread = None
        self.is_active = False
        self.configured_services = []

        # Güvenlik önlemi: Script aniden kapansa bile proxy'yi kapat
        atexit.register(self.disable_protection)

    def get_network_services(self):
        """Aktif ağ servislerini listeler (Wi-Fi, Thunderbolt vb.)"""
        try:
            out = subprocess.check_output(
                ["networksetup", "-listallnetworkservices"], text=True
            ).splitlines()
            services = [
                s.strip()
                for s in out
                if s.strip()
                and not s.startswith("An asterisk")
                and not s.startswith("*")
            ]
            return services
        except Exception as e:
            print(f"[NetworkManager] Ağ servisleri alınamadı: {e}")
            return ["Wi-Fi"]

    def start_pac_server(self):
        """Yerel PAC HTTP sunucusunu başlatır"""
        if self.server:
            return

        class ReusableTCPServer(socketserver.TCPServer):
            allow_reuse_address = True

        self.server = ReusableTCPServer(("127.0.0.1", self.port), PacHandler)
        self.server_thread = threading.Thread(
            target=self.server.serve_forever, daemon=True
        )
        self.server_thread.start()
        print(f"[NetworkManager] PAC Sunucusu {self.pac_url} adresinde aktif.")

    def enable_protection(self):
        """macOS sisteminde PAC proxy'yi aktif eder"""
        if self.is_active:
            return

        self.start_pac_server()
        services = self.get_network_services()
        self.configured_services = []

        for svc in services:
            try:
                # URL ata ve aktif et
                subprocess.run(
                    ["networksetup", "-setautoproxyurl", svc, self.pac_url],
                    check=True,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
                subprocess.run(
                    ["networksetup", "-setautoproxystate", svc, "on"],
                    check=True,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
                self.configured_services.append(svc)
            except Exception as e:
                print(f"[NetworkManager] {svc} servisi yapılandırılamadı: {e}")

        self.is_active = True
        print(f"[NetworkManager] Korumalar devreye alındı ({', '.join(self.configured_services)}).")

    def disable_protection(self):
        """PAC proxy'yi devre dışı bırakır ve sunucuyu kapatır"""
        if not self.is_active:
            return

        services = self.configured_services or self.get_network_services()
        for svc in services:
            try:
                subprocess.run(
                    ["networksetup", "-setautoproxystate", svc, "off"],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
            except Exception:
                pass

        if self.server:
            try:
                self.server.shutdown()
                self.server.server_close()
            except Exception:
                pass
            self.server = None

        self.is_active = False
        print("[NetworkManager] Korumalar tamamen kaldırıldı, sistem normale döndü.")
