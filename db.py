import os
from contextlib import contextmanager

import psycopg2
import psycopg2.extras

# Cấu hình khi chạy trên máy cá nhân (localhost)
DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "dbname": "gyusachi",
    "user": "postgres",
    "password": "Ngoc010306"
}

# Biến môi trường từ Render (khi đưa lên web)
DATABASE_URL = os.environ.get("DATABASE_URL")


def get_conn():
    if DATABASE_URL:
        return psycopg2.connect(DATABASE_URL)
    return psycopg2.connect(**DB_CONFIG)


def query(sql, params=None, one=False):
    """Lấy dữ liệu (SELECT). Trả về list dict, hoặc 1 dict nếu one=True."""
    conn = get_conn()
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(sql, params)
            rows = cur.fetchall()
            return (rows[0] if rows else None) if one else rows
    finally:
        conn.close()


def execute(sql, params=None):
    """Ghi dữ liệu (INSERT / UPDATE / DELETE). Nếu có RETURNING thì trả về dòng đó."""
    conn = get_conn()
    try:
        with conn:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                cur.execute(sql, params)
                if cur.description:
                    return cur.fetchone()
    finally:
        conn.close()


@contextmanager
def transaction():
    """Dùng khi cần nhiều lệnh ghi LIÊN TIẾP mà phải thành công cùng nhau."""
    conn = get_conn()
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            yield cur
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()