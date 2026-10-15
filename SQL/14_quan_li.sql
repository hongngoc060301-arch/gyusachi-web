-- =====================================================
-- 14. QUẢN LÍ: thêm cột bật/tắt món gọi lẻ (hết hàng)
-- Chạy SAU file 13. Chạy lại nhiều lần không sao.
-- Lưu ý: file 10 có TRUNCATE alacarte_items -> nếu chạy lại 10 thì giá bạn đã sửa
-- trên trang Quản lí sẽ về giá gốc, và phải chạy lại 11 rồi 14.
-- =====================================================

ALTER TABLE alacarte_items ADD COLUMN IF NOT EXISTS is_active BOOLEAN NOT NULL DEFAULT TRUE;

CREATE INDEX IF NOT EXISTS idx_orders_paid_date ON orders ((paid_at::date));

-- Kiểm tra: cột is_active có mặt, tất cả món đang bán
SELECT COUNT(*) AS so_mon, COUNT(*) FILTER (WHERE is_active) AS dang_ban FROM alacarte_items;
