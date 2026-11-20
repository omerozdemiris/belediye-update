# Aşama 2 — Veritabanı, Config ve `public/upload` Aktarımı

## 1. `config/files.php` Güncellemesi
* Kaynak projenin `images` tablosunda aktif veri bulunan `type` ID'leri (`34`, `35`, `36` vb.) hedef projenin `config/files.php` dosyasında farklı modüllerle çakışıyorsa:
  * Hedef projede boş olan modüllerin ID'lerini başka boş numaralara kaydır (örn. `37`, `38`).
  * Kaynağın aktif `type` ID'lerini ve `dosya_dizinleri` karşılıklarını hedef `config/files.php` içerisine birebir ekle.

## 2. Veritabanı Aktarımı (`scripts/migrate_db.py`)
* **Eksik Tablolar:** Kaynakta olup hedefte olmayan tablolar `SHOW CREATE TABLE <KAYNAK_DB>.<table>` ile hedef DB'de oluşturulur.
* **Ortak Kolonlar:** Her tablo için `ortak_kolonlar = [c for c in kaynak_cols if c in hedef_cols]` hesaplanır ve:
  ```sql
  SET SESSION sql_mode='';
  SET FOREIGN_KEY_CHECKS=0;
  INSERT INTO <HEDEF_DB>.`<table>` (...) SELECT ... FROM <KAYNAK_DB>.`<table>`;
  ```
* **Duplicate `slug` Hatası (`1062`):** Kaynakta `slug` alanı unique olmayan tablolarda (ör. `haberler`) hedefte `UNIQUE` index varsa:
  ```sql
  ALTER TABLE `<table>` DROP INDEX slug, ADD INDEX slug (slug);
  ```
  ardından tablo tekrar aktarılır.
* **Pasif Kayıt Kontrolü (`durum = 0`):** Aktarım sonrası `duyurular`, `haberler`, `slayt`, `tarihimerkezler` gibi ana sayfa tablolarında tüm kayıtların `durum = 0` olup olmadığı kontrol edilir. Hedefte `where('durum', 1)` ile çekiliyorsa kullanıcıya sorularak `durum = 1` yapılır.

## 3. `public/upload/` Dosya Senkronizasyonu
```bash
rsync -a --exclude='.DS_Store' <KAYNAK_PROJE>/public/upload/ <HEDEF_PROJE>/public/upload/
```
* Klasör adı farklılığı varsa (örn. kaynakta `kardessehirler`, hedefte `kardes_sehirler` kullanılıyorsa) ilgili alt klasör de ayrıca hedef klasör adına kopyalanır:
  ```bash
  rsync -a --exclude='.DS_Store' <KAYNAK_PROJE>/public/upload/kardessehirler/ <HEDEF_PROJE>/public/upload/kardes_sehirler/
  ```
* Aktarım sonunda her iki taraftaki dosya sayıları karşılaştırılır (`0` eksik doğrulaması).
