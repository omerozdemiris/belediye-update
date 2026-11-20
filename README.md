# Belediye Update — Laravel Belediye Projesi Veri & Kimlik Taşıma Kiti

## Amaç
Bu klasör, aynı veya %95 benzer mimariye sahip iki Laravel belediye projesi arasında (bir **Kaynak Belediye** projesinden daha yeni tasarımlı bir **Hedef Belediye** projesine) **sıfır veri kaybıyla** veri, dosya, statik içerik, kurumsal kimlik, renk ve eksik modül taşıma sürecini standartlaştırmak için hazırlanmıştır.

## İstenilen Sonuç
Taşıma tamamlandığında hedef proje:
1. Kaynak veritabanındaki **tüm aktif verileri** (haberler, duyurular, meclis kararları/gündemleri, basında biz, kurslar, müdürlükler, muhtarlıklar, tarihi merkezler, webtv, menüler, içerikler vb.) eksiksiz barındırır.
2. `public/upload/` altındaki **tüm medya ve ek dosyaları** (PDF, resim, galeri) kırık link olmadan sunar.
3. Eski belediyeye ait hiçbir metin, il/ilçe adı, e-posta, harici e-belediye/kent rehberi linki, dosya adı veya eski kurumsal renk barındırmaz.
4. Yerel IP üzerinde `php artisan serve --host <IP>` ile ayağa kalkar, tüm menü linkleri `200 OK` döner.

---

## Klasör Yapısı

```text
belediye_update/
├── SKILL.md                              # Agent ana talimat ve zorunlu kurallar dosyası
├── README.md                             # Genel bakış, amaç, kullanım ve uyarılar
├── docs/
│   ├── 01_analiz_ve_hazirlik.md          # Ortam kontrolü, temizlik ve şema karşılaştırma
│   ├── 02_veritabani_ve_upload_aktarimi.md # DB aktarımı, config/files.php ve upload/ senkronu
│   ├── 03_env_statik_veriler_ve_arayuz.md  # .env, statik görseller, renkler, YouTube, arama
│   └── 04_eksik_mvc_ve_dogrulama.md      # Eksik MVC ekleme, null kontrolleri ve HTTP testleri
└── scripts/
    ├── compare_schemas.py                # İki DB arasındaki tablo, kolon ve type farklarını listeler
    ├── migrate_db.py                     # Eksik tabloları açar, ortak kolonları kayıpsız aktarır
    └── verify_links_and_files.py         # Menü linklerini HTTP ile ve ek dosyaları diskte doğrular
```

---

## Ön Koşullar
* Yerel MySQL sunucusu açık olmalı ve hem kaynak hem hedef `.sql` dosyaları veritabanı olarak yüklenmiş olmalı.
* Her iki projenin kaynak kodları aynı çalışma dizini altında bulunmalı.
* Python 3, `rsync` ve PHP/Laravel CLI erişilebilir olmalı.

---

## Dikkat Edilmesi Gereken Kritik Noktalar
1. **Çakışmalarda Sormadan İlerleme:** Kolon farkları, `config/files.php` `type` ID çakışmaları (`34, 35, 36` gibi) ve klasör isim farkları (`kardessehirler` vs `kardes_sehirler`) mutlaka kullanıcıya sorularak çözülmelidir.
2. **Aktif vs Pasif Kayıtlar:** Kaynakta tüm kayıtlar `durum = 0` olabilir (örn. `duyurular`). Hedef `HomeController` `durum = 1` bekliyorsa kullanıcı onayıyla güncellenmelidir.
3. **Hardcoded ID'ler:** Hedef projedeki Blade dosyalarında eski belediyeye ait sabit ID'ler olabilir (örn. `/tarihi-merkezler/tarihi-merkezler/1`, `BaskanGaleri::findOrFail(6)`, `/fotograflar/kelkit/20`). Bunlar mutlaka dinamik rotalara veya gerçek kayıt sorgularına çevrilmelidir.
4. **HTTPS Zorlaması:** Hedef `AppServiceProvider.php` içindeki `URL::forceScheme('https')` yerel sunucuda görsellerin kırılmasına yol açar; `config('app.env') !== 'local'` koşuluna bağlanmalıdır.
5. **Sayfa Kaynağı Temizliği:** `kelkitbgkirmizi.png` gibi eski belediye adını taşıyan statik dosya adları da yeniden adlandırılmalı ve HTML kaynağında eski belediye adına dair `0` eşleşme kaldığı doğrulanmalıdır.
6. **Yönetim Paneli (`mt-admin`) Eşitleme ve `.env` Auth:** `AUTH_USER` / `AUTH_PASS` değişken adları (`UserAuth` middleware ile uyumlu) yeni belediyeye göre güncellenip `php artisan config:clear` yapılmalı; `config/log.php` eksik anahtarları tamamlanmalı; `mt-admin/parts/sidebar.blade.php` menüleri kaynak paneldeki aktif/kapalı durumuna göre eşitlenmelidir.
