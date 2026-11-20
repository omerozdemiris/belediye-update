# Aşama 4 & 5 — Eksik MVC Yapıları, Özel Sayfalar ve Doğrulama

## 1. Eksik MVC Modüllerinin Eklenmesi
Kaynak projede verisi bulunan ancak hedef projede karşılığı olmayan modüller (`basindabiz`, `meclisgundemi`, `kurslar`, `webtv`, `kvkk`, `hakimiyet-i-milliye` vb.):
* **Model & Controller:** Kaynak proje tablo yapısına göre Model ve Admin Controller oluşturulur; Frontend Controller ise hedef projenin mevcut benzer Controller'ı (örn. `HaberController`, `MeclisKarariController`) örnek alınarak yazılır.
* **Blade Şablonları:**
  * Liste/detay haber benzeri modüller (`basindabiz`, `kurslar`) hedef projenin `haberler.blade.php` ve `haber.blade.php` şablonlarından uyarlanır.
  * Meclis listesi modülleri (`meclisgundemi`) hedef projenin `mecliskararlari.blade.php` şablonundan uyarlanır.
  * Admin (`mt-admin`) view'ları eklenip `sidebar.blade.php` ve `routes/admin.php` ile bağlanır.

## 1.5. Yönetim Panelleri (`mt-admin`) Karşılaştırma ve Sidebar Eşitleme
1. Kaynak ve hedef `resources/views/mt-admin/parts/sidebar.blade.php` dosyaları karşılaştırılır:
   * **Kaynakta Aktif / Hedefte `"Kapalı"` Olanlar:** Kaynak yönetim panelinde aktif olan ancak hedefte `"Kapalı"` rozetiyle pasif duran modüller (ör. `WebTV`, `Kurslar`) kullanıcı onayından sonra `"Kapalı"` rozeti kaldırılıp ilgili `route('admin.*.index')` bağlantıları verilerek aktif edilir (mükerrer satır bırakılmaz).
   * **Hedefte Aktif / Kaynakta Olmayan veya Kapalı Olanlar:** Kaynak panelde bulunmayan veya kapalı olan modüller (ör. `Hızlı Menü`, `Çalışmalarımız`, `Dahili Telefon Listesi`, `Mobil Uygulama`, `Otobüs Güzergahları`) kullanıcı onayıyla Blade yorumu (`{{-- ... --}}`) içine alınarak gizlenir.
2. İşlem sonrası `php artisan view:clear` çalıştırılır ve `/mt-admin` girişi (`AUTH_USER`/`AUTH_PASS` + `users` tablosu) test edilir.

## 2. Sık Karşılaşılan Özel Sayfa Uyumsuzlukları
* **Başkan Sayfası (`BaskanController` & `sayfalar/baskan/index.blade.php`):**
  * Sabit ID ile çekilen galeri (`findOrFail(6)`) yerine `Image::where('type', config('files.dosya_turleri.baskangaleri'))` sorgusu kullan.
  * `baskangaleri` yolunun `upload/raporlardosyalar/` değil `upload/baskangaleri/` olduğundan emin ol.
  * `baskanvideolari` tablosunda video sütunu `link` değil `video` (tam YouTube URL) olabilir; regex ile 11 haneli YouTube ID ayıkla (`videohelper` alias hatasına dikkat et).
* **Gezilecek Yerler / Tarihi Merkezler ("Tümünü Gör"):**
  * Hardcoded `/tarihi-merkezler/tarihi-merkezler/1` gibi eski kategori ID'li linkleri `route('pages.tarihi_merkezler')` yap.
* **Null Kontrollü İçerik ve Encümenler (`500` Hatalarını Önleme):**
  * `IcerikController::detay($slug)` içinde `$icerik` bulunamazsa `500` yerine boş `Icerikler` nesnesi veya `404` döndür.
  * `EncumenlerController::index()` view yolunun hedef klasör yapısıyla (`sayfalar.meclis.encumenler`) eşleştiğini doğrula.

## 3. Sunucuyu Ayağa Kaldırma ve Uçtan Uca Doğrulama
1. Cache temizle ve yerel IP üzerinde sunucuyu başlat:
   ```bash
   php artisan config:clear && php artisan route:clear && php artisan view:clear
   php artisan serve --host <LOCAL_IP> --port 8000
   ```
2. `scripts/verify_links_and_files.py http://<LOCAL_IP>:8000 <HEDEF_DB> <HEDEF_PROJE>` çalıştır:
   * Veritabanındaki `menuler` tablosunda yer alan tüm iç linklerin HTTP `200 OK` döndüğünü doğrula.
   * `images` tablosundaki tüm kayıtların fiziksel dosyalarının diskte mevcut olduğunu doğrula.
   * Ana sayfa HTML kaynağında eski belediyeye ait kelimelerin `0` olduğunu doğrula.
