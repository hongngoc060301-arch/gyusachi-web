-- =====================================================
-- BẢNG DỮ LIỆU A LA CARTE (gồm cả thức uống gọi lẻ)
-- Chạy SAU file 09. Chạy lại thì xoá sạch và nhập lại từ đầu (phải chạy lại file 11).
-- =====================================================

CREATE TABLE IF NOT EXISTS alacarte_items (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    category VARCHAR(100),
    station_code VARCHAR(10),
    price NUMERIC(10, 2) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Xóa dữ liệu cũ (nếu chạy lại script) để tránh trùng lặp
TRUNCATE TABLE alacarte_items RESTART IDENTITY CASCADE;

-- ---------- 1. Khai vị (ST04) ----------
INSERT INTO alacarte_items (name, category, station_code, price) VALUES
('Rong Biển Trộn Mè', 'Khai vị', 'ST04', 68000),
('Dưa Leo Tổng Hợp', 'Khai vị', 'ST04', 25000),
('Dưa Trộn', 'Khai vị', 'ST04', 58000),
('Đậu Nành Nhật', 'Khai vị', 'ST04', 35000),
('Lá Rong Biển', 'Khai vị', 'ST04', 18000),
('Da Cá Hồi Chiên', 'Khai vị', 'ST04', 78000),
('Trứng Cút Ngâm', 'Khai vị', 'ST04', 45000),
('Đậu Phộng Rang Muối', 'Khai vị', 'ST04', 39000);

-- ---------- 2. Salad (ST04) ----------
INSERT INTO alacarte_items (name, category, station_code, price) VALUES
('Salad Thanh Cua', 'Salad', 'ST04', 78000),
('Salad Truyền Thống', 'Salad', 'ST04', 88000),
('Salad Da Cá Hồi Chiên', 'Salad', 'ST04', 88000),
('Salad Cá Hồi', 'Salad', 'ST04', 98000),
('Gyusachi Salad', 'Salad', 'ST04', 88000),
('Salad Hải Sản', 'Salad', 'ST04', 98000),
('Salad Rong Biển', 'Salad', 'ST04', 79000),
('Salad Hành', 'Salad', 'ST04', 79000),
('Salad Gà', 'Salad', 'ST04', 78000);

-- ---------- 3. Thịt nướng (ST03) ----------
INSERT INTO alacarte_items (name, category, station_code, price) VALUES
-- Bò (Trang 2 & 3)
('Diềm Bò Cao Cấp', 'Thịt nướng', 'ST03', 98000),
('Nạc Vai Bò Cao Cấp', 'Thịt nướng', 'ST03', 218000),
('Diềm Thăn Bò', 'Thịt nướng', 'ST03', 158000),
('Diềm Thăn Đế Vương', 'Thịt nướng', 'ST03', 218000),
('Sườn Bò', 'Thịt nướng', 'ST03', 155000),
('Gầu Bò', 'Thịt nướng', 'ST03', 98000),
('Nạc Vai', 'Thịt nướng', 'ST03', 118000),
('Dẻ sườn bò', 'Thịt nướng', 'ST03', 128000),
('Thăn Ngoại Bò', 'Thịt nướng', 'ST03', 109000),
('Ba Chỉ Bò Nấm Kim Châm', 'Thịt nướng', 'ST03', 68000),
('Ba Chỉ Bò Nấm Đùi Gà', 'Thịt nướng', 'ST03', 68000),
('Ba Chỉ Bò Cuộn Măng Tây', 'Thịt nướng', 'ST03', 69000),
('Ba Chỉ Bò Cuốn Đậu Bắp', 'Thịt nướng', 'ST03', 68000),
('Tokyu Wagyu', 'Thịt nướng', 'ST03', 485000),
('Tokusen Gyusachi Karubi', 'Thịt nướng', 'ST03', 138000),
('Sườn Bò Không Xương', 'Thịt nướng', 'ST03', 168000),
('Ba Chỉ Bò Mỏng', 'Thịt nướng', 'ST03', 98000),
('Lõi Vai Bò', 'Thịt nướng', 'ST03', 108000),
('Ba Chỉ Bò Dày', 'Thịt nướng', 'ST03', 89000),
('Ba Chỉ Bò Mỹ', 'Thịt nướng', 'ST03', 78000),
('Bắp Bò Hoa', 'Thịt nướng', 'ST03', 89000),
('Lưỡi Bò Hoa', 'Thịt nướng', 'ST03', 138000),
('Lưỡi Bò', 'Thịt nướng', 'ST03', 118000),
('Gyusachi Karubi', 'Thịt nướng', 'ST03', 98000),
-- Gà, Heo & Đồ nướng khác (Trang 4)
('Thịt Cổ Gà Sốt Miso', 'Thịt nướng', 'ST03', 78000),
('Thịt Cổ Gà Sốt Muối', 'Thịt nướng', 'ST03', 78000),
('Thịt Cổ Gà Sốt Momi', 'Thịt nướng', 'ST03', 78000),
('Ba Chỉ Heo', 'Thịt nướng', 'ST03', 69000),
('Tỏi Nướng Giấy Bạc', 'Thịt nướng', 'ST03', 28000),
('Da Gà', 'Thịt nướng', 'ST03', 68000),
('Bắp Nướng Bơ', 'Thịt nướng', 'ST03', 48000),
('Sườn Heo', 'Thịt nướng', 'ST03', 78000),
('Diềm Heo', 'Thịt nướng', 'ST03', 78000),
('Thăn Heo', 'Thịt nướng', 'ST03', 88000),
('Phomai Nướng Giấy Bạc', 'Thịt nướng', 'ST03', 49000),
('Ba Chỉ Heo Khổ Lớn', 'Thịt nướng', 'ST03', 68000),
('Nọng Heo', 'Thịt nướng', 'ST03', 78000),
('Xúc Xích', 'Thịt nướng', 'ST03', 78000),
('Thịt gà', 'Thịt nướng', 'ST03', 58000),
('Cánh Gà', 'Thịt nướng', 'ST03', 58000),
('Lưỡi Heo', 'Thịt nướng', 'ST03', 68000),
('Dồi Sụn', 'Thịt nướng', 'ST03', 58000);
-- ---------- 4. Sets Thịt Nướng (ST03) ----------
INSERT INTO alacarte_items (name, category, station_code, price) VALUES
('Set Thịt Tổng Hợp 1', 'Set Thịt Nướng', 'ST03', 299000),
('Set Thịt Tổng Hợp 2', 'Set Thịt Nướng', 'ST03', 388000),
('Set Thịt Tổng Hợp 3', 'Set Thịt Nướng', 'ST03', 199000);

-- ---------- 5. Hải Sản Nướng (ST03) ----------
INSERT INTO alacarte_items (name, category, station_code, price) VALUES
('Cá Hồi Nướng Giấy Bạc', 'Hải sản nướng', 'ST03', 118000),
('Cá Saba Nướng', 'Hải sản nướng', 'ST03', 78000),
('Mực', 'Hải sản nướng', 'ST03', 88000),
('Bạch Tuộc', 'Hải sản nướng', 'ST03', 78000),
('Tôm', 'Hải sản nướng', 'ST03', 98000);

-- ---------- 6. Sushi (ST04) ----------
INSERT INTO alacarte_items (name, category, station_code, price) VALUES
('Sushi Lươn', 'Sushi', 'ST04', 159000),
('Nigiri Cá Hồi Nướng Trứng Tôm', 'Sushi', 'ST04', 79000),
('Nigiri Bơ Cá Hồi', 'Sushi', 'ST04', 89000),
('Nigiri Lươn', 'Sushi', 'ST04', 89000),
('Sushi Cá Hồi Nướng Phomai', 'Sushi', 'ST04', 129000),
('Nigiri Cá Hồi Mayo', 'Sushi', 'ST04', 79000),
('Nigiri Cá Trích', 'Sushi', 'ST04', 89000),
('Nigiri Bạch Tuộc', 'Sushi', 'ST04', 59000),
('Sushi Truyền Thống', 'Sushi', 'ST04', 108000),
('Nigiri Cá Hồi', 'Sushi', 'ST04', 79000),
('Nigiri Cá Ngừ', 'Sushi', 'ST04', 58000),
('Nigiri Trứng', 'Sushi', 'ST04', 58000),
('Sushi Cá Hồi Nướng', 'Sushi', 'ST04', 119000),
('Nigiri Cá Ngừ Nướng', 'Sushi', 'ST04', 58000),
('Nigiri Thanh Cua', 'Sushi', 'ST04', 68000),
('Sushi Cá Hồi', 'Sushi', 'ST04', 119000),
('Nigiri Cá Hồi Nướng', 'Sushi', 'ST04', 79000),
('Nigiri Tôm', 'Sushi', 'ST04', 79000),
('Nigiri Bò', 'Sushi', 'ST04', 69000),
('Sushi Trứng Tôm', 'Sushi', 'ST04', 109000),
('Sushi Chiên', 'Sushi', 'ST04', 89000);

-- ---------- 7. Sashimi (ST02) ----------
INSERT INTO alacarte_items (name, category, station_code, price) VALUES
('Sashimi Cá Kiếm', 'Sashimi', 'ST02', 98000),
('Sashimi Cá Trích', 'Sashimi', 'ST02', 119000),
('Sashimi Cá Ngừ', 'Sashimi', 'ST02', 98000),
('Sashimi Cá Kiếm Khè Lửa', 'Sashimi', 'ST02', 98000),
('Sashimi Cá Hồi', 'Sashimi', 'ST02', 139000),
('Sashimi Bạch Tuộc', 'Sashimi', 'ST02', 98000),
('Sashimi Tổng Hợp', 'Sashimi', 'ST02', 219000),
('Trứng Cá Trứng', 'Sashimi', 'ST02', 58000),
('Cá Ngừ Đại Dương/Negi', 'Sashimi', 'ST02', 78000);

-- ---------- 8. Cơm (ST05) ----------
INSERT INTO alacarte_items (name, category, station_code, price) VALUES
('Cơm Trộn Truyền Thống', 'Cơm', 'ST05', 129000),
('Cơm Chiên Hải Sản', 'Cơm', 'ST05', 119000),
('Cơm Lươn', 'Cơm', 'ST05', 189000),
('Cơm Trộn Gyusachi', 'Cơm', 'ST05', 129000),
('Cơm Trộn Cá Hồi', 'Cơm', 'ST05', 129000),
('Cơm Chiên Cá Hồi', 'Cơm', 'ST05', 98000),
('Cơm Chiên Bò', 'Cơm', 'ST05', 98000),
('Cơm Chiên Trứng', 'Cơm', 'ST05', 88000),
('Cơm Thịt Bò Xào', 'Cơm', 'ST05', 88000),
('Cơm Thịt Bằm', 'Cơm', 'ST05', 88000);
-- ---------- 9. Pizza (ST05) ----------
INSERT INTO alacarte_items (name, category, station_code, price) VALUES
('Pizza Ngô', 'Pizza', 'ST05', 79000),
('Pizza Phomai', 'Pizza', 'ST05', 89000);

-- ---------- 10. Mỳ (ST05) ----------
INSERT INTO alacarte_items (name, category, station_code, price) VALUES
('Mì Udon Trứng Cá Tuyết', 'Mì', 'ST05', 98000),
('Mì Udon Xào Hải Sản', 'Mì', 'ST05', 98000),
('Mì Xào Bò', 'Mì', 'ST05', 78000),
('Mì Xào Hải Sản', 'Mì', 'ST05', 78000),
('Mì Udon Xào Bò', 'Mì', 'ST05', 89000),
('Mì Udon Xào Kim Chi', 'Mì', 'ST05', 78000),
('Mì Udon Miso', 'Mì', 'ST05', 68000),
('Mì Udon Kimchi', 'Mì', 'ST05', 78000),
('Mì Lạnh', 'Mì', 'ST05', 89000),
('Mì Lạnh Kim Chi', 'Mì', 'ST05', 89000);

-- ---------- 11. Lẩu & Topping (ST05) ----------
INSERT INTO alacarte_items (name, category, station_code, price) VALUES
('Lẩu Hải Sản & Thịt Thập Cẩm', 'Lẩu', 'ST05', 168000),
('Lẩu Thịt Thập Cẩm', 'Lẩu', 'ST05', 138000),
('Lẩu Hải Sản', 'Lẩu', 'ST05', 148000),
('Lẩu Hải Sản và Thịt Tổng Hợp', 'Lẩu', 'ST05', 495000),
-- Topping Lẩu
('Mì tôm (Topping)', 'Topping', 'ST05', 15000),
('Mì nhật (Topping)', 'Topping', 'ST05', 28000),
('Mì udon (Topping)', 'Topping', 'ST05', 28000),
('Ba Rọi Heo (Topping)', 'Topping', 'ST05', 62000),
('Ba Chỉ Bò Mỹ (Topping)', 'Topping', 'ST05', 78000),
('Nghêu (Topping)', 'Topping', 'ST05', 39000),
('Tôm (Topping)', 'Topping', 'ST05', 82000),
('Mực (Topping)', 'Topping', 'ST05', 79000),
('Bạch Tuộc (Topping)', 'Topping', 'ST05', 69000),
('Nấm Tổng Hợp (Topping)', 'Topping', 'ST05', 38000),
('Lườn Cá Hồi (Topping)', 'Topping', 'ST05', 62000),
('Đậu Hũ (Topping)', 'Topping', 'ST05', 15000),
('Cải Thảo (Topping)', 'Topping', 'ST05', 15000);

-- ---------- 12. Món ăn thêm (ST05) ----------
INSERT INTO alacarte_items (name, category, station_code, price) VALUES
('Khoai lang chiên', 'Món ăn thêm', 'ST05', 48000),
('Khoai lang lắc phomai', 'Món ăn thêm', 'ST05', 58000),
('Tôm Chiên Xù', 'Món ăn thêm', 'ST05', 68000),
('Bạch Tuộc Chiên Giòn', 'Món ăn thêm', 'ST05', 79000),
('Heo Chiên Xù', 'Món ăn thêm', 'ST05', 79000),
('Thịt Xào Gừng', 'Món ăn thêm', 'ST05', 98000),
('Sụn Gà Chiên', 'Món ăn thêm', 'ST05', 88000),
('Cánh gà chiên', 'Món ăn thêm', 'ST05', 69000),
('Thịt heo xiên', 'Món ăn thêm', 'ST05', 69000),
('Gà rán chiên xù', 'Món ăn thêm', 'ST05', 78000),
('Da gà chiên', 'Món ăn thêm', 'ST05', 78000),
('Gà rán truyền thống', 'Món ăn thêm', 'ST05', 89000),
('Gà rán lắc phomai', 'Món ăn thêm', 'ST05', 98000),
('Gà Rán Cay', 'Món ăn thêm', 'ST05', 98000),
('Bánh xèo', 'Món ăn thêm', 'ST05', 89000),
('Há cảo chiên', 'Món ăn thêm', 'ST05', 59000),
('Takoyaki', 'Món ăn thêm', 'ST05', 69000),
('Khoai lang kén', 'Món ăn thêm', 'ST05', 59000),
('Pho mai viên', 'Món ăn thêm', 'ST05', 59000),
('Khoai tây chiên', 'Món ăn thêm', 'ST05', 48000),
('Khoai tây lắc phomai', 'Món ăn thêm', 'ST05', 58000),
('Phomai que', 'Món ăn thêm', 'ST05', 59000),
('Gà sốt teriyaki', 'Món ăn thêm', 'ST05', 78000);

-- ---------- 13. Soup (ST05) ----------
INSERT INTO alacarte_items (name, category, station_code, price) VALUES
('Soup Miso', 'Soup', 'ST05', 19000),
('Soup Rong Biển', 'Soup', 'ST05', 19000),
('Soup Cay', 'Soup', 'ST05', 68000),
('Soup Trứng', 'Soup', 'ST05', 28000);

-- ---------- 14. Kim chi (ST04) ----------
INSERT INTO alacarte_items (name, category, station_code, price) VALUES
('Kim Chi Dưa Leo', 'Kim chi', 'ST04', 19000),
('Kim Chi Cải Thảo', 'Kim chi', 'ST04', 29000);
-- =====================================================
-- 15. THỨC UỐNG GỌI LẺ (trạm pha chế ST01, giá chưa gồm VAT)
-- =====================================================

-- ---------- 15.1 Soda ----------
INSERT INTO alacarte_items (name, category, station_code, price) VALUES
('Soda Chanh',       'Soda', 'ST01', 32000),
('Soda Chanh Dây',   'Soda', 'ST01', 32000),
('Soda Việt Quất',   'Soda', 'ST01', 32000),
('Soda Đào',         'Soda', 'ST01', 32000),
('Soda Bưởi',        'Soda', 'ST01', 32000),
('Soda Vải',         'Soda', 'ST01', 32000),
('Soda Xoài',        'Soda', 'ST01', 32000),
('Soda Dưa Lưới',    'Soda', 'ST01', 32000),
('Soda Nho',         'Soda', 'ST01', 32000),
('Soda Lựu',         'Soda', 'ST01', 32000);

-- ---------- 15.2 Nước trái cây ----------
INSERT INTO alacarte_items (name, category, station_code, price) VALUES
('Nước Ép Dưa Hấu',  'Nước trái cây', 'ST01', 39000),
('Nước Cam Vắt',     'Nước trái cây', 'ST01', 39000),
('Nước Táo',         'Nước trái cây', 'ST01', 29000);

-- ---------- 15.3 Cocktail ----------
INSERT INTO alacarte_items (name, category, station_code, price) VALUES
('Cocktail Việt Quất',   'Cocktail', 'ST01', 45000),
('Cocktail Bưởi',        'Cocktail', 'ST01', 45000),
('Cocktail Đào',         'Cocktail', 'ST01', 45000),
('Cocktail Chanh Dây',   'Cocktail', 'ST01', 45000),
('Cocktail Vải',         'Cocktail', 'ST01', 45000),
('Cocktail Nho',         'Cocktail', 'ST01', 45000),
('Cocktail Nho Cam',     'Cocktail', 'ST01', 45000),
('Cocktail Haiball',     'Cocktail', 'ST01', 45000),
('Coca Haiball',         'Cocktail', 'ST01', 55000),
('Jisakei Lemon Sawa',   'Cocktail', 'ST01', 45000),
('Ume Shyu Cocktail',    'Cocktail', 'ST01', 45000);

-- ---------- 15.4 Trà ----------
INSERT INTO alacarte_items (name, category, station_code, price) VALUES
('Trà Đào',            'Trà', 'ST01', 39000),
('Trà Chanh Sả',       'Trà', 'ST01', 39000),
('Trà Vải Hoa Hồng',   'Trà', 'ST01', 39000),
('Trà Gừng Nha Đam',   'Trà', 'ST01', 39000),
('Trà Nhài',           'Trà', 'ST01', 19000),
('Trà Olong',          'Trà', 'ST01', 19000),
('Trà Lipton',         'Trà', 'ST01', 19000),
('Trà Gừng',           'Trà', 'ST01', 19000);

-- ---------- 15.5 Nước ngọt ----------
INSERT INTO alacarte_items (name, category, station_code, price) VALUES
('Pepsi',        'Nước ngọt', 'ST01', 25000),
('Pepsi Lemon',  'Nước ngọt', 'ST01', 25000),
('Cocacola',     'Nước ngọt', 'ST01', 25000),
('7Up',          'Nước ngọt', 'ST01', 25000),
('Sprite',       'Nước ngọt', 'ST01', 25000),
('Soda',         'Nước ngọt', 'ST01', 20000),
('Soda Sipha',   'Nước ngọt', 'ST01', 25000),
('Aquafina',     'Nước ngọt', 'ST01', 18000);

-- ---------- 15.6 Rượu ----------
INSERT INTO alacarte_items (name, category, station_code, price) VALUES
('Owari Otokoyama 160ml',                       'Rượu', 'ST01',    95000),
('Etsu No Hajime 300ml',                        'Rượu', 'ST01',   228000),
('Etsu No Hajime 1800ml',                       'Rượu', 'ST01',   785000),
('Soju',                                        'Rượu', 'ST01',    98000),
('Ume Shyu Choya 720ml',                        'Rượu', 'ST01',   798000),
('Ume Shyu Choya (Glass)',                      'Rượu', 'ST01',    78000),
('Iichiko 720ml',                               'Rượu', 'ST01',   998000),
('Iichiko (Glass)',                             'Rượu', 'ST01',    98000),
('Hakutsuru Junmai Nigori Sayuri 720ml',        'Rượu', 'ST01',   685000),
('Hakutsuru Junmai Nigori Sayuri 300ml',        'Rượu', 'ST01',   389000),
('Kuro Kirishima 1800ml',                       'Rượu', 'ST01',  1798000),
('Kuro Kirishima (Glass)',                      'Rượu', 'ST01',    98000),
('Kinryu No Mai Junkinpakuiri (Gold) 1800ml',   'Rượu', 'ST01',  1089000),
('Hakushika Nama 300ml',                        'Rượu', 'ST01',   289000),
('Sawanotsuru Deluxe 720ml',                    'Rượu', 'ST01',   758000),
('Kuro Kirishima Imo 900ml',                    'Rượu', 'ST01',   998000),
('Makkoli',                                     'Rượu', 'ST01',   135000),
('Kubota Junmai Ginjo 720ml',                   'Rượu', 'ST01',   998000),
('Kubota Senju 720ml',                          'Rượu', 'ST01',   948000),
('Kubota Senju 300ml',                          'Rượu', 'ST01',   485000),
('Kinmiya Shochu 720ml',                        'Rượu', 'ST01',   789000),
('Kinmiya Shochu (Glass)',                      'Rượu', 'ST01',    78000),
('Junmai Kongorikishi',                         'Rượu', 'ST01',   698000);

-- ---------- 15.7 Bia ----------
INSERT INTO alacarte_items (name, category, station_code, price) VALUES
('Heineken Beer',  'Bia', 'ST01', 29000),
('Tiger Beer',     'Bia', 'ST01', 27000),
('Sapporo',        'Bia', 'ST01', 39000);

-- ---------- 16. Combo (Các Set Lớn) ----------
INSERT INTO alacarte_items (name, category, station_code, price) VALUES
('Couple Combo', 'Combo', 'ST03', 499000),
('Family Combo', 'Combo', 'ST03', 845000),
('Premium Combo', 'Combo', 'ST03', 1285000);


-- ---------- Kiểm tra ----------
-- Tổng số món theo nhóm
SELECT category, COUNT(*) AS so_mon
FROM alacarte_items
GROUP BY category
ORDER BY MIN(id);
