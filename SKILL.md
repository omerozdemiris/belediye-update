---
name: belediye-update
description: İki Laravel belediye (veya benzer mimarili) projesi ile veritabanları arasında kayıpsız veri, public/upload dosya, statik görsel, renk, .env link, eksik MVC ve arayüz taşıma/giydirme rehberi ve otomasyonu.
---

# Belediye Update Skill (Kayıpsız Proje & Veri Taşıma Standardı)

Bu skill, bir **kaynak** Laravel belediye projesindeki (`KAYNAK_PROJE`, `KAYNAK_DB`) tüm verileri, dosyaları, statik görselleri, harici linkleri ve eksik modülleri; daha güncel tasarıma sahip **hedef** Laravel belediye projesine (`HEDEF_PROJE`, `HEDEF_DB`) **kayıpsız** şekilde aktarmak ve hedef projeyi yeni belediyenin kurumsal kimliğiyle ayağa kaldırmak için kullanılır.

---

## Temel Çalışma Prensibi (Zorunlu Kurallar)

1. **Farklılık ve Çakışmalarda Dur ve Sor:**
   * Tablo/kolon farkları, `config/files.php` içindeki `dosya_turleri` ID çakışmaları, `upload/` klasör isim farkları, verisi boş veya pasif (`durum = 0`) kayıtlar, menü şişmesine yol açacak ek sayfalar veya eksik modüller tespit edildiğinde **kullanıcıya sormadan bir adım dahi atma**.
   * Her aşamadan önce tespit edilen çakışmaları madde madde sun ve onay al.

2. **Otomatik Uygulanacak Standart Teknik Düzeltmeler:**
   Aşağıdaki teknik sorunlar bu mimaride standart olarak ortaya çıkar ve tespit edildiğinde doğrudan uygulanır (yine de yapılan işlem raporlanır):
   * **Yerel MySQL İstemcisi:** Homebrew MySQL istemcisi `mysql_native_password` hatası verirse sistemdeki XAMPP/MariaDB istemcisini (`/Applications/XAMPP/xamppfiles/bin/mysql`) kullan.
   * **Yerel HTTP / Canlı HTTPS (`AppServiceProvider.php`):** `URL::forceScheme('https')` koşulsuz aktifse `php artisan serve` üzerinde görseller `https://` ile üretilip kırılır. `if (config('app.env') !== 'local') { \URL::forceScheme('https'); }` şeklinde güncelle.
   * **Duplicate `slug` Unique Kısıtı:** Kaynak veritabanında tekrarlı `slug` içeren tablolarda (ör. `haberler`) hedef tablodaki `UNIQUE` index aktarımı engelliyorsa `DROP INDEX slug, ADD INDEX slug (slug)` ile normal index'e çevirerek veriyi kayıpsız aktar.
   * **YouTube Embed `referrerpolicy`:** Tüm frontend `<iframe ... youtube.com/embed ...>` etiketlerine canlıda embed hatası (Error 153 vb.) almamak için `referrerpolicy="strict-origin-when-cross-origin"` ekle.
   * **Null Kontrollü Controller'lar:** `IcerikController::detay` gibi slug/id ile tek kayıt çeken metotlarda kayıt bulunamadığında `500` hatası vermemesi için null kontrolü ekle.
   * **`config/log.php` Anahtar Doğrulaması:** `app/` altında kullanılan tüm `config('log.*')` anahtarlarının (`kullanici`, `baskangaleri`, `kurslar`, `webtv`, `fotograflar` vb.) hedef `config/log.php` içinde tanımlı olduğunu doğrula; eksikleri mevcut ID'lerle çakışmayacak yeni numaralarla ekle (`Column 'kategori' cannot be null` hatasını önler).
   * **`.env` Basic Auth (`AUTH_USER` / `AUTH_PASS`):** `UserAuth` middleware'inin okuduğu `AUTH_USER` ve `AUTH_PASS` değişken adlarını (alt çizgili biçimini bozmadan) yeni belediyeye göre güncelle; değişiklik sonrası `php artisan config:clear` yap ve `php artisan serve` sürecini yeniden başlat.

3. **Aktif Kullanılan Dosyaları Referans Al:**
   * Kaynak projedeki statik görsel, buton ve harici linkleri ararken yalnızca aktif olarak `include` edilmiş ve yorum satırına alınmamış Blade dosyalarını referans al. Eski/yorumlu kalıntıları taşıma.

4. **Ek Kod Üretmekten Kaçın:**
   * Renk değişimlerinde yeni CSS sınıfları icat etmek yerine mevcut Tailwind config ve sınıf/hex karşılıklarını doğrudan yeni renklerle değiştir.
   * Eksik MVC eklerken hedef projenin kendi mevcut Blade şablonlarını ve Controller/Model kalıplarını birebir örnek al.

---

## Standart Taşıma Aşamaları

Her taşıma işleminde aşağıdaki 5 aşamayı sırasıyla uygula:

1. **Aşama 1 — Analiz ve Ön Temizlik** → Bkz. [01_analiz_ve_hazirlik.md](docs/01_analiz_ve_hazirlik.md)
   * Ortam, DB bağlantısı, `scripts/compare_schemas.py` ile tablo/kolon/`images.type`/`upload/` farklarının çıkarılması.
   * Kullanıcı onayı sonrası hedef DB tablolarının (`migrations` hariç) `TRUNCATE` edilmesi ve `HEDEF_PROJE/public/upload/` altındaki klasör yapısını koruyarak dosyaların silinmesi.

2. **Aşama 2 — Veritabanı, Config ve `public/upload` Aktarımı** → Bkz. [02_veritabani_ve_upload_aktarimi.md](docs/02_veritabani_ve_upload_aktarimi.md)
   * `config/files.php` içindeki `dosya_turleri` ve `dosya_dizinleri` tanımlarının kaynağa uyarlanması.
   * `scripts/migrate_db.py` ile eksik tabloların oluşturulması ve ortak kolonlar üzerinden tüm verilerin aktarılması.
   * `rsync` ile `KAYNAK_PROJE/public/upload/` dosyalarının `HEDEF_PROJE/public/upload/` altına kopyalanması ve farklı isimli klasörlerin (`kardessehirler` → `kardes_sehirler` vb.) eşlenmesi.

3. **Aşama 3 — `.env`, Statik Görseller, Linkler, Renkler ve Arayüz** → Bkz. [03_env_statik_veriler_ve_arayuz.md](docs/03_env_statik_veriler_ve_arayuz.md)
   * `.env` kurum adı, il/ilçe, DB ayarları, e-belediye / Web TV / Kent Rehberi / GA linklerinin tanımlanması.
   * `public/assets/images/` içindeki logo, favicon, başkan imzası, arka plan ve yükleniyor görsellerinin eşlenmesi ve eski belediye adını taşıyan dosya adlarının yeniden adlandırılması.
   * Blade ve Controller dosyalarındaki eski belediye/il/adres/e-posta metinlerinin, renk kodlarının, YouTube `referrerpolicy` özelliklerinin ve arama modalı/sayfasının (`max-h` + `overflow-y-auto` + Tailwind layout) güncellenmesi.

4. **Aşama 4 — Eksik MVC Yapıları, Yönetim Paneli Eşitleme ve Özel Sayfalar** → Bkz. [04_eksik_mvc_ve_dogrulama.md](docs/04_eksik_mvc_ve_dogrulama.md)
   * Kaynakta verisi olup hedefte bulunmayan modüllerin (`basindabiz`, `meclisgundemi`, `kurslar`, `webtv`, `kvkk` vb.) hedef proje kalıplarıyla eklenmesi.
   * **Yönetim Panelleri (`mt-admin`) Karşılaştırma ve Sidebar Eşitleme:** Kaynak ve hedef `mt-admin/parts/sidebar.blade.php` dosyalarının kıyaslanması; kaynakta aktif olup hedefte `"Kapalı"` olan menülerin kullanıcı onayıyla açılması, hedefte olup kaynakta olmayan/kapalı olan menülerin gizlenmesi.
   * Başkan sayfası (`BaskanController`), Tarihi Merkezler ("Tümünü Gör" hardcoded ID temizliği), Encümenler ve İçerik null kontrollerinin düzeltilmesi.

5. **Aşama 5 — Sunucu Ayağa Kaldırma ve Uçtan Uca Doğrulama** → Bkz. [04_eksik_mvc_ve_dogrulama.md](docs/04_eksik_mvc_ve_dogrulama.md)
   * `php artisan serve --host <LOCAL_IP>` ile sunucunun başlatılması.
   * `scripts/verify_links_and_files.py` ile veritabanındaki tüm menü linklerinin HTTP `200`, ek dosyaların diskte eksiksiz ve HTML kaynağında eski belediye adının `0` olduğunun doğrulanması.
