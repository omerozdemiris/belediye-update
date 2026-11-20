#!/usr/bin/env python3
"""
Hedef projenin menuler tablosundaki tüm iç linkleri HTTP üzerinden test eder
ve images tablosundaki tüm dosyaların diskte mevcut olduğunu doğrular.
Kullanım: python3 verify_links_and_files.py <base_url> <hedef_db> <hedef_proje_path>
"""
import os
import shutil
import subprocess
import sys

def find_mysql():
    xampp = "/Applications/XAMPP/xamppfiles/bin/mysql"
    if os.path.exists(xampp):
        return xampp
    return shutil.which("mysql") or "mysql"

MYSQL_BIN = find_mysql()

def query(sql):
    out = subprocess.check_output([MYSQL_BIN, "-h", "127.0.0.1", "-u", "root", "-N", "-B", "-e", sql], text=True)
    return [line.split("\t") for line in out.strip().split("\n") if line]

def main():
    if len(sys.argv) != 4:
        print("Kullanım: python3 verify_links_and_files.py <base_url> <hedef_db> <hedef_proje_path>")
        sys.exit(1)

    base_url = sys.argv[1].rstrip("/")
    db = sys.argv[2]
    proj_path = sys.argv[3].rstrip("/")

    # 1. Menü linklerini test et
    menus = query(f"SELECT id, name, link FROM `{db}`.menuler WHERE link IS NOT NULL AND link != '' AND link != '#'")
    broken = []
    for mid, name, link in menus:
        if link.startswith("http"):
            continue
        url = link if link.startswith("/") else "/" + link
        code = subprocess.check_output(["curl", "-s", "-o", "/dev/null", "-w", "%{http_code}", f"{base_url}{url}"], text=True).strip()
        if code != "200":
            broken.append((mid, name, url, code))

    print(f"Menü linkleri kontrol edildi ({len(menus)} adet). Hatalı link sayısı: {len(broken)}")
    for b in broken:
        print("  HATA:", b)

    # 2. Fiziksel dosyaları kontrol et
    rows = query(f"SELECT id, type, path, name FROM `{db}`.images")
    public_dir = os.path.join(proj_path, "public")
    missing_files = [r for r in rows if not os.path.exists(public_dir + r[2] + r[3])]
    print(f"images tablosu kontrol edildi ({len(rows)} kayıt). Eksik dosya sayısı: {len(missing_files)}")
    for m in missing_files[:10]:
        print("  EKSİK DOSYA:", m)

if __name__ == "__main__":
    main()
