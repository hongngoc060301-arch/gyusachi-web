import os
from pathlib import Path
import psycopg2

DATABASE_URL = "postgresql://gyusachi_j1ah_user:QATHpWCLNHK4cBbfHZrJsHOJIBrpYFnY@dpg-db8553aj9qps73bmo0kg-a.singapore-postgres.render.com/gyusachi_j1ah"

conn = psycopg2.connect(DATABASE_URL)
conn.autocommit = True
cur = conn.cursor()

# Kiểm tra xem có file backup đơn lẻ không, nếu không thì nạp thư mục SQL/
backup_file = Path("gyusachi_backup.sql")
sql_dir = Path("SQL")

if backup_file.exists():
    print("Tìm thấy file gyusachi_backup.sql, đang nạp...")
    with open(backup_file, "r", encoding="utf-8", errors="ignore") as f:
        cur.execute(f.read())
elif sql_dir.exists():
    print("Đang nạp toàn bộ các file trong thư mục SQL/...")
    sql_files = sorted(sql_dir.glob("*.sql"))
    for file_path in sql_files:
        print(f" -> Đang chạy: {file_path.name}")
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            cur.execute(f.read())
else:
    print("LỖI: Không tìm thấy file backup lẫn thư mục SQL!")

cur.close()
conn.close()
print("\n===> NẠP DỮ LIỆU THÀNH CÔNG! <===")