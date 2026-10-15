-- =====================================================
-- 03. HÀM NHẬP MÓN: add_to_package   (BẢN SỬA: không phân biệt HOA/thường)
-- Chạy SAU file 02. Chỉ cần chạy 1 lần.
--
-- Cách dùng, mỗi món một dòng:
--   SELECT add_to_package(giá, 'Tên món', 'Nhóm', 'Mã trạm');
-- Món chưa có thì tự thêm, có rồi (kể cả viết hoa khác) thì chỉ gắn vào gói.
-- Ví dụ 'Lá Rong Biển' và 'Lá rong biển' được coi là MỘT món.
-- =====================================================

-- Chặn trùng tên không phân biệt hoa/thường ngay ở mức bảng
CREATE UNIQUE INDEX IF NOT EXISTS ux_menu_items_name_lower
    ON menu_items (LOWER(name));

CREATE OR REPLACE FUNCTION add_to_package(
    p_price   INT,
    p_name    TEXT,
    p_cat     TEXT,
    p_station TEXT
) RETURNS void AS $$
DECLARE
    mid INT;
BEGIN
    SELECT id INTO mid FROM menu_items WHERE LOWER(name) = LOWER(p_name);

    IF mid IS NULL THEN
        INSERT INTO menu_items (name, category, station_id)
        VALUES (p_name, p_cat, p_station)
        RETURNING id INTO mid;
    END IF;

    INSERT INTO package_items (package_id, menu_item_id)
    SELECT id, mid FROM packages WHERE price = p_price
    ON CONFLICT DO NOTHING;
END;
$$ LANGUAGE plpgsql;

-- Thử: phải ra  la rong biển  (nếu ra chữ hoa còn nguyên Ế/Ể... thì DB đang dùng locale C, báo mình)
SELECT LOWER('Lá Rong Biển Ế') AS thu_lower;
