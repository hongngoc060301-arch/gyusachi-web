import os
import sys
from pathlib import Path
import psycopg2

# Địa chỉ database lấy từ biến môi trường (KHÔNG ghi mật khẩu vào file này).
#   Windows (PowerShell): $env:DATABASE_URL = "postgresql://user:matkhau@host/dbname"
DATABASE_URL = os.environ.get("DATABASE_URL")
if not DATABASE_URL:
    sys.exit("LỖI: chưa đặt biến môi trường DATABASE_URL.")

# Cảnh báo: file 01_tao_bang.sql XOÁ SẠCH toàn bộ bảng (đơn hàng, hoá đơn, đặt bàn...) rồi tạo lại.
print("Database đích:", DATABASE_URL.split("@")[-1])
if input("Việc này sẽ XOÁ TOÀN BỘ dữ liệu hiện có. Gõ XOA để tiếp tục: ").strip() != "XOA":
    sys.exit("Đã huỷ, không thay đổi gì.")

conn = psycopg2.connect(DATABASE_URL)
conn.autocommit = True
cur = conn.cursor()

# Kiểm tra xem có file backup đơn lẻ không, nếu không thì nạp thư mục SQL/
backup_file = Path("gyusachi_backup.sql")
sql_dir = Path("SQL")

if backup_file.exists():
    print("Tìm thấy file gyusachi_backup.sql, đang nạp...")
    with open(backup_file, "r", encoding="utf-8") as f:     # không dùng errors="ignore" để lỗi mã hoá hiện ra rõ
        cur.execute(f.read())
elif sql_dir.exists():
    print("Đang nạp toàn bộ các file trong thư mục SQL/...")
    sql_files = sorted(sql_dir.glob("*.sql"))
    for file_path in sql_files:
        print(f" -> Đang chạy: {file_path.name}")
        with open(file_path, "r", encoding="utf-8") as f:
            cur.execute(f.read())
else:
    sys.exit("LỖI: Không tìm thấy file backup lẫn thư mục SQL!")

cur.close()
conn.close()
print("\n===> NẠP DỮ LIỆU THÀNH CÔNG! <===")