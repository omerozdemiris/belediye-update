# Aşama 1 — Analiz, Karşılaştırma ve Ön Temizlik

## 1. Ortam ve Veritabanı İstemcisi Kontrolü
* Çalışma dizinindeki proje klasörlerini (`KAYNAK_PROJE`, `HEDEF_PROJE`) ve `.sql` yedeklerini listele.
* MySQL bağlantısını test et:
  ```bash
  mysql -h 127.0.0.1 -u root -e "SHOW DATABASES;"
  ```
* **Not:** macOS ortamında Homebrew `mysql` istemcisi `Authentication plugin 'mysql_native_password' cannot be loaded` hatası verirse XAMPP/MariaDB istemcisini kullan:
  ```bash
  /Applications/XAMPP/xamppfiles/bin/mysql -h 127.0.0.1 -u root -e "SHOW DATABASES;"
  ```

## 2. Şema, `config/files.php` ve `upload/` Karşılaştırması
Temizlik veya aktarım yapmadan önce mutlaka şu 3 kontrolü çalıştır:
1. **Veritabanı Farkları:** `scripts/compare_schemas.py <KAYNAK_DB> <HEDEF_DB>` ile:
   * Sadece kaynakta bulunan (ve veri içeren) tabloları
   * Sadece hedefte bulunan tabloları
   * Ortak tablolardaki kolon farklarını (`+ kaynakta var`, `- hedefte var`)
   * `images.type` değer dağılımını çıkar.
2. **`config/files.php` Farkları:** İki projenin `config/files.php` dosyalarındaki `dosya_turleri` ve `dosya_dizinleri` eşleşmelerini karşılaştır. Aynı ID numarasına farklı modüller atanmışsa (ör. `35` veya `36` çakışması) **kullanıcıya sor**.
3. **`public/upload/` Klasör Farkları:** İki projenin `public/upload/` alt klasörlerini listele; isim farkı olanları (`kardessehirler` vs `kardes_sehirler`) veya hedefte bulunmayan klasörleri not et.

## 3. Hedef Projenin Ön Temizliği (Kullanıcı Onayıyla)
Kullanıcı onayladığında:
1. **Dosya Temizliği (Klasörler Korunur):**
   ```bash
   find <HEDEF_PROJE>/public/upload -type f -delete
   ```
   *(Alt klasörler silinmez, yalnızca içlerindeki eski belediye dosyaları kalıcı olarak silinir.)*
2. **Veritabanı Temizliği (Şema Korunur):**
   `migrations` tablosu dışındaki tüm tablolar `SET FOREIGN_KEY_CHECKS=0` ile `TRUNCATE` edilir:
   ```bash
   mysql -h 127.0.0.1 -u root -N -e "SELECT CONCAT('TRUNCATE TABLE \`', table_name, '\`;') FROM information_schema.tables WHERE table_schema='<HEDEF_DB>' AND table_name != 'migrations';" | (echo "SET FOREIGN_KEY_CHECKS=0;"; cat; echo "SET FOREIGN_KEY_CHECKS=1;") | mysql -h 127.0.0.1 -u root <HEDEF_DB>
   ```
