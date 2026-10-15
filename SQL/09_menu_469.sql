-- =====================================================
-- 09. MENU BUFFET 469K (Cao cấp nhất)
-- Chạy SAU file 08_menu_389k.sql
-- =====================================================

-- ---------- A. Copy toàn bộ món gói 389K sang gói 469K ----------

INSERT INTO package_items (package_id, menu_item_id)
SELECT (SELECT id FROM packages WHERE price = 469000), menu_item_id
FROM package_items
WHERE package_id = (SELECT id FROM packages WHERE price = 389000)
ON CONFLICT DO NOTHING;

-- ---------- B. Thêm danh sách các món của 469K ----------

-- 1. Khai vị (ST04)
SELECT add_to_package(469000, 'Lá Rong Biển',                 'Khai vị', 'ST04');
SELECT add_to_package(469000, 'Rong Biển Trộn Mè',            'Khai vị', 'ST04');
SELECT add_to_package(469000, 'Đậu Phộng Rang Muối',          'Khai vị', 'ST04');
SELECT add_to_package(469000, 'Trứng Cút Ngâm',               'Khai vị', 'ST04');
SELECT add_to_package(469000, 'Da Cá Hồi Chiên',              'Khai vị', 'ST04');
SELECT add_to_package(469000, 'Đậu Nành Nhật',                'Khai vị', 'ST04');
SELECT add_to_package(469000, 'Dưa Leo Tổng Hợp',             'Khai vị', 'ST04');
SELECT add_to_package(469000, 'Dưa Trộn',                     'Khai vị', 'ST04');

-- 2. Salad (ST04)
SELECT add_to_package(469000, 'Salad Thịt Xông Khói',         'Salad', 'ST04');
SELECT add_to_package(469000, 'Salad Mỳ Nhật',                'Salad', 'ST04');
SELECT add_to_package(469000, 'Salad Da Cá Hồi Chiên',        'Salad', 'ST04');
SELECT add_to_package(469000, 'Salad Truyền Thống',           'Salad', 'ST04');
SELECT add_to_package(469000, 'Salad Hải Sản',                'Salad', 'ST04');
SELECT add_to_package(469000, 'Salad Cá Hồi',                 'Salad', 'ST04');
SELECT add_to_package(469000, 'Gyusachi Salad',               'Salad', 'ST04');
SELECT add_to_package(469000, 'Salad Thanh Cua',              'Salad', 'ST04');
SELECT add_to_package(469000, 'Salad Rong Biển',              'Salad', 'ST04');
SELECT add_to_package(469000, 'Salad Hành',                   'Salad', 'ST04');
SELECT add_to_package(469000, 'Salad Gà',                     'Salad', 'ST04');

-- 3. Thịt nướng (ST03)
SELECT add_to_package(469000, 'Tokusen Gyusachi Karubi',      'Thịt nướng', 'ST03');
SELECT add_to_package(469000, 'Nạc Lưng Bò',                  'Thịt nướng', 'ST03');
SELECT add_to_package(469000, 'Diềm Bò Tuyết',                'Thịt nướng', 'ST03');
SELECT add_to_package(469000, 'Diềm Thăn Bò',                 'Thịt nướng', 'ST03');
SELECT add_to_package(469000, 'Nạc Vai Bò Cao Cấp',           'Thịt nướng', 'ST03');
SELECT add_to_package(469000, 'Diềm Thăn Đế Vương',           'Thịt nướng', 'ST03');
SELECT add_to_package(469000, 'Lưỡi Bò Tare',                 'Thịt nướng', 'ST03');
SELECT add_to_package(469000, 'Lưỡi Bò Hoa',                  'Thịt nướng', 'ST03');
SELECT add_to_package(469000, 'Gyusachi Karubi',              'Thịt nướng', 'ST03');
SELECT add_to_package(469000, 'Lõi Vai Bò',                   'Thịt nướng', 'ST03');
SELECT add_to_package(469000, 'Nạc Cổ Bò',                    'Thịt nướng', 'ST03');
SELECT add_to_package(469000, 'Lưỡi Bò',                      'Thịt nướng', 'ST03');
SELECT add_to_package(469000, 'Ba Chỉ Bò Nấm Kim Châm',       'Thịt nướng', 'ST03');
SELECT add_to_package(469000, 'Ba Chỉ Bò Nấm Đùi Gà',         'Thịt nướng', 'ST03');
SELECT add_to_package(469000, 'Ba Chỉ Bò Cuộn Măng Tây',      'Thịt nướng', 'ST03');
SELECT add_to_package(469000, 'Ba Chỉ Bò Cuốn Đậu Bắp',       'Thịt nướng', 'ST03');
SELECT add_to_package(469000, 'Ba Chỉ Bò Mỏng',               'Thịt nướng', 'ST03');
SELECT add_to_package(469000, 'Ba Chỉ Bò Mỹ',                 'Thịt nướng', 'ST03');
SELECT add_to_package(469000, 'Gù Bò',                        'Thịt nướng', 'ST03');
SELECT add_to_package(469000, 'Gầu Bò',                       'Thịt nướng', 'ST03');
SELECT add_to_package(469000, 'Bắp Bò Hoa',                   'Thịt nướng', 'ST03');
SELECT add_to_package(469000, 'Ba Chỉ Bò Dày',                'Thịt nướng', 'ST03');
SELECT add_to_package(469000, 'Dẻ sườn bò',                    'Thịt nướng', 'ST03');
SELECT add_to_package(469000, 'Sườn Bò',                      'Thịt nướng', 'ST03');
SELECT add_to_package(469000, 'Ba Chỉ Heo Tam Vị',            'Thịt nướng', 'ST03');
SELECT add_to_package(469000, 'Thăn Heo',                     'Thịt nướng', 'ST03');
SELECT add_to_package(469000, 'Ba Chỉ Heo',                   'Thịt nướng', 'ST03');
SELECT add_to_package(469000, 'Ba Chỉ Heo Khổ Lớn',           'Thịt nướng', 'ST03');
SELECT add_to_package(469000, 'Cốt Lết Heo',                  'Thịt nướng', 'ST03');
SELECT add_to_package(469000, 'Lưỡi Heo',                     'Thịt nướng', 'ST03');
SELECT add_to_package(469000, 'Nầm Heo',                      'Thịt nướng', 'ST03');
SELECT add_to_package(469000, 'Nọng Heo',                     'Thịt nướng', 'ST03');
SELECT add_to_package(469000, 'Ba Chỉ Heo Mỏng',              'Thịt nướng', 'ST03');
SELECT add_to_package(469000, 'Ba Chỉ Heo Nấm Kim Châm',      'Thịt nướng', 'ST03');
SELECT add_to_package(469000, 'Sườn Heo',                     'Thịt nướng', 'ST03');
SELECT add_to_package(469000, 'Thịt gà Seseri',               'Thịt nướng', 'ST03');
SELECT add_to_package(469000, 'Cánh Gà',                      'Thịt nướng', 'ST03');
SELECT add_to_package(469000, 'Thịt gà',                           'Thịt nướng', 'ST03');
SELECT add_to_package(469000, 'Xúc Xích',                     'Thịt nướng', 'ST03');
SELECT add_to_package(469000, 'Dồi Sụn',                      'Thịt nướng', 'ST03');
SELECT add_to_package(469000, 'Tỏi Nướng Giấy Bạc',           'Thịt nướng', 'ST03');
SELECT add_to_package(469000, 'Phô mai Nướng Giấy Bạc',        'Thịt nướng', 'ST03');
SELECT add_to_package(469000, 'Bắp Nướng Bơ',                 'Thịt nướng', 'ST03');

-- 4. Hải sản nướng (ST03)
SELECT add_to_package(469000, 'Cá Saba Nướng',                'Hải sản nướng', 'ST03');
SELECT add_to_package(469000, 'Mực',                          'Hải sản nướng', 'ST03');
SELECT add_to_package(469000, 'Tôm',                          'Hải sản nướng', 'ST03');
SELECT add_to_package(469000, 'Bạch Tuộc',                    'Hải sản nướng', 'ST03');

-- 5. Sushi (ST04)
SELECT add_to_package(469000, 'Inari Cá Hồi Mayo',            'Sushi', 'ST04');
SELECT add_to_package(469000, 'Inari Cá Ngừ Mayo',            'Sushi', 'ST04');
SELECT add_to_package(469000, 'Inari Truyền Thống',           'Sushi', 'ST04');
SELECT add_to_package(469000, 'Nigiri Cá Hồi Mayo',           'Sushi', 'ST04');
SELECT add_to_package(469000, 'Nigiri Lươn',                  'Sushi', 'ST04');
SELECT add_to_package(469000, 'Inari Phô mai Nướng',           'Sushi', 'ST04');
SELECT add_to_package(469000, 'Nigiri Cá Hồi Nướng Trứng Tôm','Sushi', 'ST04');
SELECT add_to_package(469000, 'Nigiri Cá Hồi Nướng',          'Sushi', 'ST04');
SELECT add_to_package(469000, 'Nigiri Cá Hồi',                'Sushi', 'ST04');
SELECT add_to_package(469000, 'Nigiri Bạch Tuộc',             'Sushi', 'ST04');
SELECT add_to_package(469000, 'Nigiri Bò',                    'Sushi', 'ST04');
SELECT add_to_package(469000, 'Nigiri Bơ Cá Hồi',             'Sushi', 'ST04');
SELECT add_to_package(469000, 'Nigiri Cá Trích',              'Sushi', 'ST04');
SELECT add_to_package(469000, 'Nigiri Cá Ngừ Nướng',          'Sushi', 'ST04');
SELECT add_to_package(469000, 'Nigiri Cá Ngừ',                'Sushi', 'ST04');
SELECT add_to_package(469000, 'Nigiri Tôm',                   'Sushi', 'ST04');
SELECT add_to_package(469000, 'Nigiri Trứng',                 'Sushi', 'ST04');
SELECT add_to_package(469000, 'Nigiri Thanh Cua',             'Sushi', 'ST04');
SELECT add_to_package(469000, 'Sushi Lươn',                   'Sushi', 'ST04');
SELECT add_to_package(469000, 'Sushi Cá Hồi',                 'Sushi', 'ST04');
SELECT add_to_package(469000, 'Sushi Chiên',                  'Sushi', 'ST04');
SELECT add_to_package(469000, 'Sushi Cá Hồi Nướng',           'Sushi', 'ST04');
SELECT add_to_package(469000, 'Sushi Truyền Thống',           'Sushi', 'ST04');
SELECT add_to_package(469000, 'Sushi Cá Hồi Nướng Phô mai',    'Sushi', 'ST04');
SELECT add_to_package(469000, 'Sushi Trứng Tôm',              'Sushi', 'ST04');

-- 6. Sashimi (ST02) 
SELECT add_to_package(469000, 'Sashimi Cá Kiếm',              'Sashimi', 'ST02');
SELECT add_to_package(469000, 'Sashimi Cá Trích',             'Sashimi', 'ST02');
SELECT add_to_package(469000, 'Sashimi Cá Ngừ',               'Sashimi', 'ST02');
SELECT add_to_package(469000, 'Sashimi Cá Kiếm Khè Lửa',      'Sashimi', 'ST02');
SELECT add_to_package(469000, 'Sashimi Cá Hồi',               'Sashimi', 'ST02');
SELECT add_to_package(469000, 'Sashimi Bạch Tuộc',            'Sashimi', 'ST02');
SELECT add_to_package(469000, 'Sashimi Tổng Hợp',             'Sashimi', 'ST02');
SELECT add_to_package(469000, 'Trứng Cá Trứng',               'Sashimi', 'ST02');
SELECT add_to_package(469000, 'Cá Ngừ Đại Dương/Negi',        'Sashimi', 'ST02');

-- 7. Lẩu (ST05)
SELECT add_to_package(469000, 'Lẩu Bò Gyusachi',              'Lẩu', 'ST05');
SELECT add_to_package(469000, 'Lẩu Thịt Cừu',                 'Lẩu', 'ST05');
SELECT add_to_package(469000, 'Lẩu Hải Sản & Thịt Thập Cẩm',  'Lẩu', 'ST05');
SELECT add_to_package(469000, 'Lẩu Hải Sản',                  'Lẩu', 'ST05');
SELECT add_to_package(469000, 'Lẩu Thịt Thập Cẩm',            'Lẩu', 'ST05');

-- 8. Cơm (ST05)
SELECT add_to_package(469000, 'Cơm Trộn Gyusachi',            'Cơm', 'ST05');
SELECT add_to_package(469000, 'Cơm Trộn Truyền Thống',        'Cơm', 'ST05');
SELECT add_to_package(469000, 'Cơm Trộn Cá Hồi',              'Cơm', 'ST05');
SELECT add_to_package(469000, 'Cơm Chiên Cá Hồi',             'Cơm', 'ST05');
SELECT add_to_package(469000, 'Cơm Chiên Hải Sản',            'Cơm', 'ST05');
SELECT add_to_package(469000, 'Cơm Lươn',                     'Cơm', 'ST05');
SELECT add_to_package(469000, 'Cơm Chiên Bò',                 'Cơm', 'ST05');
SELECT add_to_package(469000, 'Cơm Chiên Trứng',              'Cơm', 'ST05');
SELECT add_to_package(469000, 'Cơm Thịt Bò Xào',              'Cơm', 'ST05');
SELECT add_to_package(469000, 'Cơm Thịt Bằm',                 'Cơm', 'ST05');
-- (bỏ dòng 'Cơm Trắng': món này đã có sẵn từ gói 199K)

-- 9. Pizza (ST05)
SELECT add_to_package(469000, 'Pizza Ngô',                    'Pizza', 'ST05');
SELECT add_to_package(469000, 'Pizza Phô mai',                 'Pizza', 'ST05');
SELECT add_to_package(469000, 'Pizza Gyusachi',               'Pizza', 'ST05');

-- 10. Món ăn thêm (ST05)
SELECT add_to_package(469000, 'Khoai lang chiên',             'Món ăn thêm', 'ST05');
SELECT add_to_package(469000, 'Khoai lang lắc phô mai',        'Món ăn thêm', 'ST05');
SELECT add_to_package(469000, 'Tôm Chiên Xù',                 'Món ăn thêm', 'ST05');
SELECT add_to_package(469000, 'Bạch Tuộc Chiên Giòn',         'Món ăn thêm', 'ST05');
SELECT add_to_package(469000, 'Heo Chiên Xù',                 'Món ăn thêm', 'ST05');
SELECT add_to_package(469000, 'Thịt Xào Gừng',                'Món ăn thêm', 'ST05');
SELECT add_to_package(469000, 'Sụn Gà Chiên',                 'Món ăn thêm', 'ST05');
SELECT add_to_package(469000, 'Cánh gà chiên',                'Món ăn thêm', 'ST05');
SELECT add_to_package(469000, 'Thịt heo xiên',                'Món ăn thêm', 'ST05');
SELECT add_to_package(469000, 'Gà chiên xù',                  'Món ăn thêm', 'ST05');
SELECT add_to_package(469000, 'Da gà chiên',                  'Món ăn thêm', 'ST05');
SELECT add_to_package(469000, 'Gà rán truyền thống',          'Món ăn thêm', 'ST05');
SELECT add_to_package(469000, 'Gà rán lắc phô mai',            'Món ăn thêm', 'ST05');
SELECT add_to_package(469000, 'Gà Rán Cay',                   'Món ăn thêm', 'ST05');
SELECT add_to_package(469000, 'Bánh xèo',                     'Món ăn thêm', 'ST05');
SELECT add_to_package(469000, 'Sủi Cảo Chiên',                'Món ăn thêm', 'ST05');
SELECT add_to_package(469000, 'Takoyaki',                     'Món ăn thêm', 'ST05');
SELECT add_to_package(469000, 'Khoai lang kén',               'Món ăn thêm', 'ST05');
SELECT add_to_package(469000, 'Há cảo chiên',                 'Món ăn thêm', 'ST05');
SELECT add_to_package(469000, 'Khoai tây chiên',              'Món ăn thêm', 'ST05');
SELECT add_to_package(469000, 'Khoai tây lắc phô mai',         'Món ăn thêm', 'ST05');
SELECT add_to_package(469000, 'Phô mai que',                   'Món ăn thêm', 'ST05');
SELECT add_to_package(469000, 'Gà sốt teriyaki',              'Món ăn thêm', 'ST05');

-- 11. Topping Lẩu & Đồ ăn kèm (ST05)
SELECT add_to_package(469000, 'Ba chỉ bò mỏng (Lẩu)',         'Topping', 'ST05');
SELECT add_to_package(469000, 'Bắp bò hoa (Lẩu)',             'Topping', 'ST05');
SELECT add_to_package(469000, 'Nạc vai bò mỏng (Lẩu)',        'Topping', 'ST05');
SELECT add_to_package(469000, 'Gàu bò (Lẩu)',                 'Topping', 'ST05');
SELECT add_to_package(469000, 'Ba chỉ heo mỏng (Lẩu)',        'Topping', 'ST05');
SELECT add_to_package(469000, 'Thịt cừu mỏng (Lẩu)',          'Topping', 'ST05');
SELECT add_to_package(469000, 'Bắp ngô',                      'Topping', 'ST05');
SELECT add_to_package(469000, 'Nấm kim châm',                 'Topping', 'ST05');
SELECT add_to_package(469000, 'Nấm đùi gà',                   'Topping', 'ST05');
SELECT add_to_package(469000, 'Cải thảo',                     'Topping', 'ST05');
SELECT add_to_package(469000, 'Đậu khuôn',                    'Topping', 'ST05');
SELECT add_to_package(469000, 'Đậu bắp',                      'Topping', 'ST05');
SELECT add_to_package(469000, 'Sốt Bonya củ cải',             'Topping', 'ST05');
SELECT add_to_package(469000, 'Hành Paro Muối',               'Topping', 'ST05');
SELECT add_to_package(469000, 'Bí Ngô',                       'Topping', 'ST05');
SELECT add_to_package(469000, 'Hành Tây Nướng',               'Topping', 'ST05');
SELECT add_to_package(469000, 'Khoai Lang',                   'Topping', 'ST05');
SELECT add_to_package(469000, 'Thanh Cua',                    'Topping', 'ST05');
-- (bỏ dòng 'Rau Cuộn': món này đã có sẵn từ gói 199K)
SELECT add_to_package(469000, 'Trứng',                        'Topping', 'ST05');
-- (bỏ dòng 'Món Tráng Miệng Theo Ngày': món này đã có sẵn từ gói 199K)

-- 12. Mì (dùng cho lẩu hoặc ăn kèm)
SELECT add_to_package(469000, 'Mì tôm',                       'Mì', 'ST05');
SELECT add_to_package(469000, 'Mì nhật',                      'Mì', 'ST05');
SELECT add_to_package(469000, 'Mì udon',                      'Mì', 'ST05');

-- ---------- C. Kiểm tra ----------

SELECT COUNT(*) AS so_mon_469k
FROM package_items
WHERE package_id = (SELECT id FROM packages WHERE price = 469000);

SELECT m.category, COUNT(*) AS so_mon
FROM package_items pi
JOIN menu_items m ON m.id = pi.menu_item_id
WHERE pi.package_id = (SELECT id FROM packages WHERE price = 469000)
GROUP BY m.category
ORDER BY CASE m.category
    WHEN 'Khai vị' THEN 1    WHEN 'Salad' THEN 2        WHEN 'Kim chi' THEN 3
    WHEN 'Thịt nướng' THEN 4 WHEN 'Hải sản nướng' THEN 5 WHEN 'Sashimi' THEN 6
    WHEN 'Sushi' THEN 7      WHEN 'Lẩu' THEN 8          WHEN 'Cơm' THEN 9
    WHEN 'Pizza' THEN 10     WHEN 'Mì' THEN 11          WHEN 'Món ăn thêm' THEN 12
    WHEN 'Soup' THEN 13      WHEN 'Topping' THEN 14     ELSE 15 END;