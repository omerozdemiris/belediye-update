# Aşama 3 — `.env`, Statik Görseller, Linkler, Renkler ve Arayüz

## 1. `.env` Yapılandırması ve Yönetim Paneli Şifreleri
* **Kurumsal Bilgiler:** `KURUM_ADI`, `BELEDIYE`, `APP_URL`, `ETKINLIK_URL`, `MAIL_HOST`, `MAIL_USERNAME`, `MAIL_FROM_ADDRESS` yeni belediyeye göre güncellenir.
* **Basic Auth Şifreleri (`AUTH_USER` / `AUTH_PASS`):** `app/Http/Middleware/UserAuth.php` dosyası `env('AUTH_USER')` ve `env('AUTH_PASS')` okur. `.env` içinde değişken adlarının alt çizgili (`AUTH_USER`, `AUTH_PASS`) kalmasına dikkat edilerek yeni belediye şifreleri atanır; değişiklikten sonra `php artisan config:clear` çalıştırılır ve `php artisan serve` yeniden başlatılır.
* **`config/log.php` Eşitlemesi:** `app/` altındaki tüm `config('log.*')` çağrıları (`kullanici`, `baskangaleri`, `kurslar`, `webtv`, `fotograflar` vb.) taranır ve hedef `config/log.php` içinde eksik olanlar mevcut ID'lerle çakışmayacak numaralarla eklenir.
* **Yerel DB (Geliştirme):** Yerel sunucuda test için `DB_DATABASE`, `DB_USERNAME`, `DB_PASSWORD` lokal DB bilgilerine ayarlanır (işlem sonunda kullanıcıya canlı ayarlara döndürülüp döndürülmeyeceği sorulur).
* **Harici Link Değişkenleri:** Kaynak projedeki aktif kullanılan e-belediye, Web TV, Kent Rehberi, Google Analytics ID'si `.env` içine tanımlanır:
  ```env
  EBELEDIYE_URL="..."
  EBELEDIYE_BORC_URL="..."
  EBELEDIYE_RAYIC_URL="..."
  EBELEDIYE_MALIYET_URL="..."
  EBELEDIYE_BEYAN_URL="..."
  WEBTV_URL="..."
  KENT_REHBERI_URL="#"
  GA_MEASUREMENT_ID="..."
  ```
* Blade dosyalarında tüm harici belediye linkleri `env('...', '#')` üzerinden çağrılır. Eski belediyeye ait `bulutkbs.gov.tr`, `online.<eski>.bel.tr` gibi linkler tamamen temizlenir.

## 2. `AppServiceProvider.php` (Yerel HTTP / Canlı HTTPS)
`app/Providers/AppServiceProvider.php` içinde koşulsuz `\URL::forceScheme('https');` varsa:
```php
if (config('app.env') !== 'local') {
    \URL::forceScheme('https');
}
```
olarak değiştirilir; aksi halde yerel `php artisan serve` ortamında tüm `asset()` görselleri kırılır.

## 3. Statik Görseller ve Dosya İsim Temizliği
* Kaynak projedeki aktif Blade/asset klasöründen (`public/assets/img` veya `images`) alınan görseller hedef `public/assets/images/` altına eşlenir:
  * Başkan imzası (`baskan-imza-beyaz.svg` → `baskanimza.svg`, `baskanimzabeyaz.svg`)
  * Logolar (`yatay-logo.svg` → `beyazlogo.svg`, `logo-white-text.svg`; `yatay-mavi-logo.svg` → `yatay-logo.svg`; yatay PNG → `footer.png`; ikon → `favicon.png`, `favicon.svg`)
  * Arka planlar (`footer.jpg` → `footerbg.jpg`, `header.jpg` → `header.jpg`, `menubg.jpg`)
  * Yükleniyor ikonu (`yukleniyor.svg`)
* **Eski Belediye Adlı Dosyalar:** `kelkitbgkirmizi.png`, `kelkitbg.svg`, `kelkit_logo.png` gibi dosya adları `<yeni>bgkirmizi.png` vb. olarak yeniden adlandırılır ve Blade içindeki referansları güncellenir.

## 4. Metinler ve Renk Kodları
* `resources/views/` (ve `app/Http/Controllers/`, `emails/`) içindeki eski belediye adı, il adı, adres, telefon, e-posta, eski başkan fallback isimleri ve Google Analytics ID'si yenileriyle değiştirilir.
* Kullanıcının verdiği renk dönüşümleri ek CSS yazmadan doğrudan mevcut hex/rgb ve Tailwind config (`belediye-blue` vb.) tanımları üzerinden uygulanır.

## 5. YouTube `referrerpolicy` ve Arama Sayfası
* **YouTube Iframe:** Frontend'deki tüm `<iframe ... youtube.com/embed ...>` etiketlerine `referrerpolicy="strict-origin-when-cross-origin"` eklenir.
* **Arama Modalı:** `.live-search-results-container` alanına sabit maksimum yükseklik (`max-h-[50vh] overflow-y-auto`) verilir; `live-search-results.blade.php` modal taşmasını önleyecek şekilde `w-full` akışına alınır.
* **Arama Sonuç Sayfası (`/arama`):** Tailwind içermeyen ham liste görünümü `@extends('layouts.sayfa_yeni')` ile kurumsal Tailwind tasarımına geçirilir ve `SearchController::search()` içinden `$keyword` view'a gönderilir.
