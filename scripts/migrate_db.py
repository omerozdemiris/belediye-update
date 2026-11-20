#!/usr/bin/env python3
"""
Kaynak veritabanındaki eksik tabloları hedefte oluşturur ve tüm tabloları ortak kolonlar üzerinden kayıpsız aktarır.
Kullanım: python3 migrate_db.py <kaynak_db> <hedef_db>
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
MYSQL_BASE = [MYSQL_BIN, "-h", "127.0.0.1", "-u", "root"]

def query(sql):
    out = subprocess.check_output(MYSQL_BASE + ["-N", "-B", "-e", sql], text=True)
    return [line.split("\t") for line in out.strip().split("\n") if line]

def exec_sql(sql, db):
    p = subprocess.run(MYSQL_BASE + ["-D", db], input=sql, text=True, capture_output=True)
    if p.returncode != 0:
        raise RuntimeError(p.stderr.strip())

def main():
    if len(sys.argv) != 3:
        print("Kullanım: python3 migrate_db.py <kaynak_db> <hedef_db>")
        sys.exit(1)

    src_db, dst_db = sys.argv[1], sys.argv[2]

    src_tables = sorted(r[0] for r in query(f"SELECT table_name FROM information_schema.tables WHERE table_schema='{src_db}'"))
    dst_tables = set(r[0] for r in query(f"SELECT table_name FROM information_schema.tables WHERE table_schema='{dst_db}'"))

    for t in src_tables:
        if t not in dst_tables:
            res = subprocess.check_output(MYSQL_BASE + ["-N", "-B", "-e", f"SHOW CREATE TABLE `{src_db}`.`{t}`"], text=True)
            create_stmt = res.split("\t", 1)[1].replace("\\n", "\n")
            exec_sql(f"SET FOREIGN_KEY_CHECKS=0;\n{create_stmt};\nSET FOREIGN_KEY_CHECKS=1;", dst_db)
            print(f"[CREATE] {t} oluşturuldu.")

    src_cols, dst_cols = {}, {}
    for db, store in [(src_db, src_cols), (dst_db, dst_cols)]:
        for r in query(f"SELECT table_name, column_name FROM information_schema.columns WHERE table_schema='{db}' ORDER BY table_name, ordinal_position"):
            store.setdefault(r[0], []).append(r[1])

    total, errors = 0, []
    for t in src_tables:
        cnt = int(query(f"SELECT COUNT(*) FROM `{src_db}`.`{t}`")[0][0])
        if cnt == 0:
            continue
        common = [c for c in src_cols[t] if c in dst_cols[t]]
        cols_str = ", ".join(f"`{c}`" for c in common)
        sql = (
            "SET SESSION sql_mode='';\n"
            "SET FOREIGN_KEY_CHECKS=0;\n"
            f"TRUNCATE TABLE `{t}`;\n"
            f"INSERT INTO `{dst_db}`.`{t}` ({cols_str}) SELECT {cols_str} FROM `{src_db}`.`{t}`;\n"
            "SET FOREIGN_KEY_CHECKS=1;"
        )
        try:
            exec_sql(sql, dst_db)
            new_cnt = int(query(f"SELECT COUNT(*) FROM `{dst_db}`.`{t}`")[0][0])
            print(f"[OK] {t}: {cnt} -> {new_cnt}")
            total += new_cnt
        except Exception as e:
            print(f"[ERR] {t}: {e}")
            errors.append((t, str(e)))

    print(f"\nToplam aktarılan satır: {total} | Hata sayısı: {len(errors)}")

if __name__ == "__main__":
    main()
