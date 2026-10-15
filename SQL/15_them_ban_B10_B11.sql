-- Thêm bàn B10, B11 (tầng 2) vào CSDL ĐANG CÓ, không cần xoá dữ liệu.
-- Chạy lại nhiều lần không sao. Sức chứa 4 chỗ, muốn đổi thì sửa số 4 rồi chạy.
INSERT INTO dining_tables (id, name, capacity, min_capacity, floor, type) VALUES
('B10','B10',4,1,2,'NORMAL'),
('B11','B11',4,1,2,'NORMAL')
ON CONFLICT (id) DO NOTHING;

-- Kiểm tra: phải thấy B10 và B11 (tổng 20 bàn)
SELECT id, capacity, floor FROM dining_tables WHERE id IN ('B10','B11') ORDER BY id;
SELECT COUNT(*) AS tong_so_ban FROM dining_tables;
