# 🎯 Focus Saver (Odak Koruyucu)

**Focus Saver**, belirlediğiniz odaklanma süresi boyunca dikkat dağıtıcı web sitelerini ve arama sorgularını **doğrudan ağ seviyesinde (bağlantıyı kopararak)** engelleyen macOS odaklanma aracıdır.

---

## 🌟 İki Farklı Çalışma Modu

Focus Saver hem **macOS Sistem Düzeyinde (Safari + Chrome + Tüm Sistem)** hem de bağımsız **Tarayıcı Eklentisi** olarak çalışabilir:

### 1. 🍎 macOS Menü Çubuğu Uygulaması (Seçenek C - Önerilen)
Xcode gerektirmez! Mac'inizin üst menü çubuğuna (saat/pil yanına) yerleşir.
* **Tüm Tarayıcılarda Geçerli:** **Safari**, **Google Chrome**, **Brave**, **Arc** fark etmeksizin tüm sistemi korur.
* **Doğrudan Bağlantı Kesintisi (PAC Proxy):** Yasaklı sitelere istek atıldığında ağ seviyesinde istek reddedilir (`Sunucuya bağlanılamadı`).
* **Anlık Arama & Sekme Denetimi:** Safari veya Chrome'da `youtube`, `kick`, `twitch`, `instagram` aratıldığı anda o sekme anında kapatılır.
* **🎵 YouTube Music İstisnası:** `music.youtube.com` kesintisiz çalışır.

#### Nasıl Çalıştırılır?
* **Yöntem 1 (Masaüstünden Çift Tık):**  
  Masaüstünüzde oluşturulan `Focus Saver.command` dosyasına çift tıklayın. Menü çubuğunda **`🎯 Focus`** ikonu belirecektir.
* **Yöntem 2 (Terminal):**
  ```bash
  python3 /Users/macbookm4pro/.gemini/antigravity/scratch/focus-saver/focus_app.py
  ```
* **Yöntem 3 (Terminal CLI Sayacı):**
  ```bash
  python3 /Users/macbookm4pro/.gemini/antigravity/scratch/focus-saver/focus_cli.py 25
  ```

---

### 2. 🧩 Google Chrome Eklenti Modu (Manifest V3)
Sadece Chromium tarayıcılarda bağımsız eklenti olarak kullanmak isterseniz:
1. `chrome://extensions` adresine gidin.
2. Sağ üstten **Geliştirici modu**nu açın.
3. **Paketlenmemiş öğe yükle** diyerek Masaüstündeki `focus-saver` kısayolunu seçin.

---

## 🚫 Kural & Engelleme Matrisi

| Platform / İstek | Durum | Davranış |
| :--- | :--- | :--- |
| **YouTube (`youtube.com`, `youtu.be`)** | 🛑 Engelli | Ağ bağlantısı anında kesilir, sekme düşürülür |
| **YouTube Music (`music.youtube.com`)** | ✅ **Serbest** | Hiçbir kısıtlama uygulanmaz |
| **Kick (`kick.com`)** | 🛑 Engelli | Ağ bağlantısı anında kesilir |
| **Twitch (`twitch.tv`)** | 🛑 Engelli | Ağ bağlantısı anında kesilir |
| **Instagram (`instagram.com`)** | 🛑 Engelli | Ağ bağlantısı anında kesilir |
| **Google / Safari / Bing Aramaları** | 🛑 Engelli | Hedef kelimeler aratıldığında arama sekmesi kapanır |

---

## 🏗️ Proje Mimarisi

```
focus-saver/
├── focus_app.py               # macOS Menü Çubuğu Uygulaması (rumps tabanlı)
├── focus_cli.py               # Terminal Sayaç Arayüzü (rich progress bar)
├── core/
│   ├── network_manager.py     # macOS PAC Proxy sunucusu ve autoproxyurl kontrolü
│   ├── tab_watcher.py         # Safari ve Chrome sekmelerini izleyen AppleScript motoru
│   └── session_manager.py     # Sayaç, bildirimler ve durum yönetimi
├── manifest.json              # Chromium Manifest V3 eklenti manifestosu
├── background.js              # Eklenti Service Worker
├── rules/rules.json           # DeclarativeNetRequest kuralları
└── popup/                     # Eklenti karanlık mod arayüzü
```
