-- =====================================================
-- 17. QUẢN LÍ NÂNG CAO: nhân viên, đặt bàn, bàn, gói buffet, mật khẩu
-- Chạy SAU file 16. Chạy lại nhiều lần không sao (IF NOT EXISTS).
-- =====================================================

-- Khoá / ẩn thay vì xoá (xoá sẽ làm mất lịch sử hoá đơn)
ALTER TABLE staffs        ADD COLUMN IF NOT EXISTS is_active BOOLEAN NOT NULL DEFAULT TRUE;
ALTER TABLE dining_tables ADD COLUMN IF NOT EXISTS is_active BOOLEAN NOT NULL DEFAULT TRUE;
ALTER TABLE packages      ADD COLUMN IF NOT EXISTS is_active BOOLEAN NOT NULL DEFAULT TRUE;

-- Mật khẩu thu ngân / quản lí sau khi đổi (lưu dạng băm, không lưu chữ thật)
CREATE TABLE IF NOT EXISTS app_settings (
    key        VARCHAR(50) PRIMARY KEY,
    value      TEXT NOT NULL,
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Đơn đặt bàn
CREATE TABLE IF NOT EXISTS reservations (
    id            SERIAL PRIMARY KEY,
    customer_name VARCHAR(100) NOT NULL,
    phone         VARCHAR(20)  NOT NULL,
    guests        INT NOT NULL,
    table_id      VARCHAR(10) NOT NULL REFERENCES dining_tables(id),
    reserve_date  DATE NOT NULL,
    reserve_time  TIME NOT NULL,
    note          VARCHAR(300),
    status        VARCHAR(12) NOT NULL DEFAULT 'PENDING',   -- PENDING | CONFIRMED | ARRIVED | NO_SHOW | CANCELLED
    source        VARCHAR(10) NOT NULL DEFAULT 'WEB',        -- WEB (khách tự đặt) | STAFF (nhân viên nhập)
    created_at    TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at    TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_reservations_date  ON reservations (reserve_date, reserve_time);
CREATE INDEX IF NOT EXISTS idx_reservations_table ON reservations (table_id, reserve_date);

-- Kiểm tra: 3 cột is_active + 2 bảng mới
SELECT
  (SELECT COUNT(*) FROM information_schema.columns
    WHERE column_name = 'is_active' AND table_name IN ('staffs','dining_tables','packages')) AS so_cot_is_active,
  (SELECT COUNT(*) FROM information_schema.tables
    WHERE table_name IN ('app_settings','reservations')) AS so_bang_moi;
