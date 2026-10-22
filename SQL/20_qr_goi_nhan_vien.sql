-- =====================================================
-- 22. QR GỌI MÓN TẠI BÀN + GỌI NHÂN VIÊN / XIN TÍNH TIỀN
-- Chạy SAU file 19 (có thể chạy khi chưa chạy 20, 21). Chạy lại nhiều lần không sao (IF NOT EXISTS).
-- =====================================================

-- Yêu cầu của khách ở bàn: gọi nhân viên (CALL) hoặc xin tính tiền (BILL)
CREATE TABLE IF NOT EXISTS service_calls (
    id         SERIAL PRIMARY KEY,
    table_id   VARCHAR(10) NOT NULL REFERENCES dining_tables(id),
    order_id   INT REFERENCES orders(id) ON DELETE SET NULL,
    kind       VARCHAR(4)  NOT NULL CHECK (kind IN ('CALL', 'BILL')),
    status     VARCHAR(4)  NOT NULL DEFAULT 'OPEN' CHECK (status IN ('OPEN', 'DONE')),
    created_at TIMESTAMP   NOT NULL DEFAULT NOW(),
    done_at    TIMESTAMP,
    done_by    VARCHAR(50)
);
CREATE INDEX IF NOT EXISTS idx_service_calls_open ON service_calls (status, created_at);

-- Món do khách tự gọi qua QR sẽ có source = 'QR' (phục vụ nhìn thấy nhãn QR); phục vụ gọi là 'STAFF'
ALTER TABLE order_items ADD COLUMN IF NOT EXISTS source VARCHAR(5) NOT NULL DEFAULT 'STAFF';

-- Kiểm tra: kết quả phải là 1 và 1
SELECT
  (SELECT COUNT(*) FROM information_schema.tables  WHERE table_name = 'service_calls') AS bang_yeu_cau,
  (SELECT COUNT(*) FROM information_schema.columns WHERE table_name = 'order_items' AND column_name = 'source') AS cot_source;
