-- 1. Tạo bảng chứa chi tiết các món trong Combo
CREATE TABLE IF NOT EXISTS combo_details (
    id SERIAL PRIMARY KEY,
    combo_id INT REFERENCES alacarte_items(id) ON DELETE CASCADE,
    item_name VARCHAR(255) NOT NULL,
    station_code VARCHAR(10) NOT NULL,
    quantity INT DEFAULT 1,
    choices TEXT            -- nếu có: các lựa chọn cách nhau bằng dấu |, phục vụ phải chọn 1 khi gọi
);

-- Xóa dữ liệu cũ nếu chạy lại
TRUNCATE TABLE combo_details RESTART IDENTITY CASCADE;

-- Tạo hàm hỗ trợ thêm món vào combo cho nhanh
CREATE OR REPLACE FUNCTION add_combo_item(
    p_combo_name VARCHAR,
    p_item_name VARCHAR,
    p_station_code VARCHAR,
    p_qty INT DEFAULT 1
) RETURNS VOID AS $$
BEGIN
    INSERT INTO combo_details (combo_id, item_name, station_code, quantity)
    SELECT id, p_item_name, p_station_code, p_qty
    FROM alacarte_items WHERE name = p_combo_name;
END;
$$ LANGUAGE plpgsql;

-- =====================================================
-- 2. TÁCH CHI TIẾT TỪNG COMBO CHO CÁC BẾP
-- =====================================================

-- ---------- COUPLE COMBO (499K) ----------
SELECT add_combo_item('Couple Combo', 'Ba chỉ bò', 'ST03');
SELECT add_combo_item('Couple Combo', 'Ba chỉ heo', 'ST03');
SELECT add_combo_item('Couple Combo', 'Nạc vai', 'ST03');
SELECT add_combo_item('Couple Combo', 'Ba chỉ bò cuộn nấm kim châm', 'ST03');
SELECT add_combo_item('Couple Combo', 'Salad da cá hồi', 'ST04');
SELECT add_combo_item('Couple Combo', 'Gà rán truyền thống', 'ST05');
SELECT add_combo_item('Couple Combo', 'Đậu nành Nhật', 'ST04');
SELECT add_combo_item('Couple Combo', 'Salad cuộn', 'ST04');
SELECT add_combo_item('Couple Combo', 'Kim chi tổng hợp', 'ST04');
SELECT add_combo_item('Couple Combo', 'Lẩu (Bò/Hải sản) - Tùy chọn', 'ST05');
SELECT add_combo_item('Couple Combo', 'Kem / Dưa hấu', 'ST01');

-- ---------- FAMILY COMBO (845K) ----------
SELECT add_combo_item('Family Combo', 'Ba chỉ bò', 'ST03');
SELECT add_combo_item('Family Combo', 'Nạc vai', 'ST03');
SELECT add_combo_item('Family Combo', 'Sườn bò có xương', 'ST03');
SELECT add_combo_item('Family Combo', 'Ba chỉ heo', 'ST03');
SELECT add_combo_item('Family Combo', 'Thăn heo bản lớn', 'ST03');
SELECT add_combo_item('Family Combo', 'Ba chỉ bò cuộn nấm kim châm', 'ST03');
SELECT add_combo_item('Family Combo', 'Salad truyền thống', 'ST04');
SELECT add_combo_item('Family Combo', 'Gà rán truyền thống', 'ST05');
SELECT add_combo_item('Family Combo', 'Khoai tây chiên', 'ST05');
SELECT add_combo_item('Family Combo', 'Đậu nành Nhật', 'ST04');
SELECT add_combo_item('Family Combo', 'Salad cuộn', 'ST04');
SELECT add_combo_item('Family Combo', 'Kim chi tổng hợp', 'ST04');
SELECT add_combo_item('Family Combo', 'Lẩu (Bò/Hải sản) - Tùy chọn', 'ST05');
SELECT add_combo_item('Family Combo', 'Kem / Dưa hấu', 'ST01');

-- ---------- PREMIUM COMBO (1.285K) ----------
SELECT add_combo_item('Premium Combo', 'Rau cuộn tổng hợp', 'ST04');
SELECT add_combo_item('Premium Combo', 'Đậu nành Nhật', 'ST04');
SELECT add_combo_item('Premium Combo', 'Salad truyền thống', 'ST04');
SELECT add_combo_item('Premium Combo', 'Kim chi tổng hợp', 'ST04');
SELECT add_combo_item('Premium Combo', 'Sashimi tổng hợp', 'ST02');
SELECT add_combo_item('Premium Combo', 'Sushi cá hồi nướng phomai', 'ST04');
SELECT add_combo_item('Premium Combo', 'Dẻ sườn', 'ST03');
SELECT add_combo_item('Premium Combo', 'Sườn bò không xương', 'ST03');
SELECT add_combo_item('Premium Combo', 'Diềm thăn bò', 'ST03');
SELECT add_combo_item('Premium Combo', 'Nạc vai bò', 'ST03');
SELECT add_combo_item('Premium Combo', 'Gà rán truyền thống', 'ST05');
SELECT add_combo_item('Premium Combo', 'Lẩu (Bò/Hải sản) - Tùy chọn', 'ST05');
SELECT add_combo_item('Premium Combo', 'Kem / Dưa hấu', 'ST01');

-- ---------- SET THỊT TỔNG HỢP 1 (199K) ----------
SELECT add_combo_item('Set Thịt Tổng Hợp 1', 'Ba chỉ bò', 'ST03');
SELECT add_combo_item('Set Thịt Tổng Hợp 1', 'Ba chỉ heo', 'ST03');
SELECT add_combo_item('Set Thịt Tổng Hợp 1', 'Nạc vai', 'ST03');

-- ---------- SET THỊT TỔNG HỢP 2 (299K) ----------
SELECT add_combo_item('Set Thịt Tổng Hợp 2', 'Ba chỉ bò', 'ST03');
SELECT add_combo_item('Set Thịt Tổng Hợp 2', 'Nạc vai', 'ST03');
SELECT add_combo_item('Set Thịt Tổng Hợp 2', 'Ba chỉ heo', 'ST03');
SELECT add_combo_item('Set Thịt Tổng Hợp 2', 'Thăn heo', 'ST03');
SELECT add_combo_item('Set Thịt Tổng Hợp 2', 'Gà', 'ST03');

-- ---------- SET THỊT TỔNG HỢP 3 (388K) ----------
SELECT add_combo_item('Set Thịt Tổng Hợp 3', 'Dẻ sườn', 'ST03');
SELECT add_combo_item('Set Thịt Tổng Hợp 3', 'Diềm thăn bò', 'ST03');
SELECT add_combo_item('Set Thịt Tổng Hợp 3', 'Sườn bò không xương', 'ST03');
-- Món lẩu trong combo: khách chọn lẩu thịt hoặc lẩu hải sản
UPDATE combo_details
SET choices = 'Lẩu Thịt Thập Cẩm|Lẩu Hải Sản'
WHERE item_name = 'Lẩu (Bò/Hải sản) - Tùy chọn';

-- Kiểm tra: số dòng chi tiết của từng combo / set
SELECT a.name, COUNT(c.id) AS so_dong
FROM alacarte_items a
JOIN combo_details c ON c.combo_id = a.id
GROUP BY a.name, a.id
ORDER BY a.id;