-- =====================================================
-- 13. THU NGÂN: thêm cột lưu hoá đơn vào bảng orders
-- Chạy SAU file 12. Chạy lại nhiều lần không sao (IF NOT EXISTS).
--
-- Khi thanh toán, hệ thống lưu lại số tiền từng phần để sau này
-- Quản lí xem báo cáo doanh thu mà không phải tính lại.
-- =====================================================

ALTER TABLE orders ADD COLUMN IF NOT EXISTS paid_at        TIMESTAMP;
ALTER TABLE orders ADD COLUMN IF NOT EXISTS payment_method VARCHAR(20);          -- CASH | CARD | TRANSFER
ALTER TABLE orders ADD COLUMN IF NOT EXISTS cashier_id     VARCHAR(10) REFERENCES staffs(id);
ALTER TABLE orders ADD COLUMN IF NOT EXISTS food_amount    INT;                  -- tiền buffet đồ ăn (giá x số khách)
ALTER TABLE orders ADD COLUMN IF NOT EXISTS drink_amount   INT;                  -- tiền buffet nước
ALTER TABLE orders ADD COLUMN IF NOT EXISTS extra_amount   INT;                  -- tiền món gọi lẻ / combo / nước lẻ
ALTER TABLE orders ADD COLUMN IF NOT EXISTS discount       INT;                  -- giảm giá (đi 4 tính 3)
ALTER TABLE orders ADD COLUMN IF NOT EXISTS vat_amount     INT;                  -- VAT 8%
ALTER TABLE orders ADD COLUMN IF NOT EXISTS total          INT;                  -- tổng khách trả
ALTER TABLE orders ADD COLUMN IF NOT EXISTS promo_note     VARCHAR(200);         -- ghi chú ưu đãi đã áp dụng

CREATE INDEX IF NOT EXISTS idx_orders_paid_at ON orders(paid_at);

-- Kiểm tra: phải thấy 10 cột mới
SELECT column_name
FROM information_schema.columns
WHERE table_name = 'orders'
  AND column_name IN ('paid_at','payment_method','cashier_id','food_amount','drink_amount',
                      'extra_amount','discount','vat_amount','total','promo_note')
ORDER BY column_name;
