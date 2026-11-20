#!/usr/bin/env python3
"""
İki MySQL veritabanı şemasını (tablo, satır sayısı, kolon farkları ve images.type dağılımı) karşılaştırır.
Kullanım: python3 compare_schemas.py <kaynak_db> <hedef_db>
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
    cmd = [MYSQL_BIN, "-h", "127.0.0.1", "-u", "root", "-N", "-B", "-e", sql]
    out = subprocess.check_output(cmd, text=True)
    return [line.split("\t") for line in out.strip().split("\n") if line]

def main():
    if len(sys.argv) != 3:
        print("Kullanım: python3 compare_schemas.py <kaynak_db> <hedef_db>")
        sys.exit(1)

    src_db, dst_db = sys.argv[1], sys.argv[2]

    src_tables = set(r[0] for r in query(f"SELECT table_name FROM information_schema.tables WHERE table_schema='{src_db}'"))
    dst_tables = set(r[0] for r in query(f"SELECT table_name FROM information_schema.tables WHERE table_schema='{dst_db}'"))

    print(f"=== SADECE KAYNAKTA ({src_db}) BULUNAN TABLOLAR ===")
    for t in sorted(src_tables - dst_tables):
        cnt = query(f"SELECT COUNT(*) FROM `{src_db}`.`{t}`")[0][0]
        print(f"  {t}: {cnt} satır")

    print(f"\n=== SADECE HEDEFTE ({dst_db}) BULUNAN TABLOLAR ===")
    for t in sorted(dst_tables - src_tables):
        print(f"  {t}")

    src_cols, dst_cols = {}, {}
    for db, store in [(src_db, src_cols), (dst_db, dst_cols)]:
        for r in query(f"SELECT table_name, column_name FROM information_schema.columns WHERE table_schema='{db}' ORDER BY table_name, ordinal_position"):
            store.setdefault(r[0], []).append(r[1])

    print("\n=== ORTAK TABLOLARDAKİ KOLON FARKLARI (kaynakta veri varsa) ===")
    for t in sorted(src_tables & dst_tables):
        cnt = int(query(f"SELECT COUNT(*) FROM `{src_db}`.`{t}`")[0][0])
        if cnt == 0:
            continue
        only_src = [c for c in src_cols[t] if c not in dst_cols[t]]
        only_dst = [c for c in dst_cols[t] if c not in src_cols[t]]
        if only_src or only_dst:
            print(f"  {t} ({cnt} satır):")
            if only_src:
                print(f"    + Sadece kaynakta: {only_src}")
            if only_dst:
                print(f"    - Sadece hedefte:  {only_dst}")

    if "images" in src_tables:
        print(f"\n=== {src_db}.images TYPE DAĞILIMI ===")
        for r in query(f"SELECT type, COUNT(*) FROM `{src_db}`.images GROUP BY type ORDER BY type"):
            print(f"  type={r[0]}: {r[1]} kayıt")

if __name__ == "__main__":
    main()
