# 📋 PM Task Board & Engineering Backlog for Claude (Software Engineer)

**Proje:** Focus Saver (Odak Koruyucu)  
**Lead PM:** Antigravity  
**Lead SE:** Claude  

---

## ✅ SPRINT 1: MVP Core (Tamamlandı)
- [x] Manifest V3 konfigürasyonu (`manifest.json`)
- [x] Ağ seviyesinde bağlantı kesme kuralları (`rules/rules.json`)
- [x] `music.youtube.com` öncelikli izin (Allowlist bypass) kuralı
- [x] YouTube, Kick, Twitch, Instagram ana kuralları
- [x] Google / DuckDuckGo / Bing arama parametresi (`q=...`) filtreleri
- [x] Service Worker zamanlayıcı motoru (`background.js`)
- [x] Chrome Alarms & Storage state senkronizasyonu
- [x] Açık yasaklı sekmeleri anında yenileyerek düşürme fonksiyonu
- [x] Dark-mode macOS odak arayüzü (`popup/`)

---

## 🚀 SPRINT 2: Engineering Backlog (Claude'un Sıradaki Görevleri)

Aşağıdaki görevleri Claude'a sırayla vererek projeyi bir üst seviyeye taşıyabilirsiniz:

### Görev 2.1: Dinamik Kara Liste Yönetimi (Custom Blacklist)
* **Açıklama:** Kullanıcının popup üzerinden istediği özel web sitelerini (örn: `twitter.com`, `reddit.com`) kara listeye ekleyebilmesi.
* **Teknik Yaklaşım:** `chrome.declarativeNetRequest.updateDynamicRules` API'si kullanılarak kullanıcı tanımlı kuralların depolanması.

### Görev 2.2: Odaklanma İstatistikleri (Focus Analytics)
* **Açıklama:** Günlük ve haftalık kaç oturum tamamlandığı ve engellenen toplam istek sayısının tutulması.
* **Teknik Yaklaşım:** `chrome.storage.local` üzerinde `stats: { completedSessions: 0, totalFocusMinutes: 0 }` sayacı.

### Görev 2.3: Safari Native App Builder Script
* **Açıklama:** Safari için `.app` uzantısını tek komutla build eden Swift/Xcode otomasyon betiği hazırlanması.
