-- =====================================================
-- 18. HUỶ HOÁ ĐƠN + NHẬT KÝ THAO TÁC
-- Chạy SAU file 17. Chạy lại nhiều lần không sao (IF NOT EXISTS).
--
-- (Cấu hình VAT / ngày lễ / giờ trưa / đi 4 tính 3 lưu chung trong bảng
--  app_settings đã có từ file 17, nên không cần tạo bảng mới.)
-- =====================================================

-- Huỷ hoá đơn: không xoá hoá đơn, chỉ đánh dấu để doanh thu loại ra mà vẫn còn dấu vết
ALTER TABLE orders ADD COLUMN IF NOT EXISTS voided_at   TIMESTAMP;
ALTER TABLE orders ADD COLUMN IF NOT EXISTS void_reason VARCHAR(300);

-- Nhật ký: ai đã làm gì (đổi giá, tắt món, huỷ hoá đơn, đổi cấu hình...)
CREATE TABLE IF NOT EXISTS audit_log (
    id     SERIAL PRIMARY KEY,
    at     TIMESTAMP NOT NULL DEFAULT NOW(),
    actor  VARCHAR(50)  NOT NULL DEFAULT 'Quản lí',
    action VARCHAR(100) NOT NULL,
    target VARCHAR(200),
    detail VARCHAR(500)
);
CREATE INDEX IF NOT EXISTS idx_audit_at ON audit_log (at DESC);

-- Kiểm tra: 2 cột mới + bảng nhật ký (kết quả phải là 2 và 1)
SELECT
  (SELECT COUNT(*) FROM information_schema.columns
    WHERE table_name = 'orders' AND column_name IN ('voided_at', 'void_reason')) AS so_cot_huy_hoa_don,
  (SELECT COUNT(*) FROM information_schema.tables WHERE table_name = 'audit_log') AS bang_nhat_ky;
