-- =====================================================
-- 08. MENU BUFFET 389K (Cao cấp nhất)
-- Chạy SAU file 07_menu_349k.sql
-- =====================================================

-- ---------- A. Copy toàn bộ món gói 349K sang gói 389K ----------

INSERT INTO package_items (package_id, menu_item_id)
SELECT (SELECT id FROM packages WHERE price = 389000), menu_item_id
FROM package_items
WHERE package_id = (SELECT id FROM packages WHERE price = 349000)
ON CONFLICT DO NOTHING;

-- ---------- B. Thêm danh sách các món của 389K ----------
-- (Các món đã có ở gói dưới sẽ tự động bị bỏ qua nếu hàm add_to_package có bắt trùng lặp)

-- 1. Khai vị (ST04)
SELECT add_to_package(389000, 'Lá Rong Biển',                 'Khai vị', 'ST04');
SELECT add_to_package(389000, 'Dưa Leo Tổng Hợp',             'Khai vị', 'ST04');
SELECT add_to_package(389000, 'Đậu Phộng Rang Muối',          'Khai vị', 'ST04');
SELECT add_to_package(389000, 'Dưa Trộn',                     'Khai vị', 'ST04');
SELECT add_to_package(389000, 'Trứng Cút Ngâm',               'Khai vị', 'ST04');
SELECT add_to_package(389000, 'Da Cá Hồi Chiên',              'Khai vị', 'ST04');
SELECT add_to_package(389000, 'Đậu Nành Nhật',                'Khai vị', 'ST04');

-- 2. Salad (ST04)
SELECT add_to_package(389000, 'Salad Thịt Xông Khói',         'Salad', 'ST04');
SELECT add_to_package(389000, 'Salad Mỳ Nhật',                'Salad', 'ST04');
SELECT add_to_package(389000, 'Salad Da Cá Hồi Chiên',        'Salad', 'ST04');
SELECT add_to_package(389000, 'Salad Truyền Thống',           'Salad', 'ST04');
SELECT add_to_package(389000, 'Salad Hải Sản',                'Salad', 'ST04');
SELECT add_to_package(389000, 'Salad Cá Hồi',                 'Salad', 'ST04');
SELECT add_to_package(389000, 'Gyusachi Salad',               'Salad', 'ST04');
SELECT add_to_package(389000, 'Salad Thanh Cua',              'Salad', 'ST04');
SELECT add_to_package(389000, 'Salad Rong Biển',              'Salad', 'ST04');
SELECT add_to_package(389000, 'Salad Hành',                   'Salad', 'ST04');
SELECT add_to_package(389000, 'Salad Gà',                     'Salad', 'ST04');

-- 3. Thịt nướng (ST03)
SELECT add_to_package(389000, 'Set Thịt Tổng Hợp 5 Loại',     'Thịt nướng', 'ST03');
SELECT add_to_package(389000, 'Gyusachi Karubi',              'Thịt nướng', 'ST03');
SELECT add_to_package(389000, 'Sườn Bò',                      'Thịt nướng', 'ST03');
SELECT add_to_package(389000, 'Ba Chỉ Bò Mỹ',                 'Thịt nướng', 'ST03');
SELECT add_to_package(389000, 'Nạc Cổ Bò',                    'Thịt nướng', 'ST03');
SELECT add_to_package(389000, 'Ba Chỉ Bò Mỏng',               'Thịt nướng', 'ST03');
SELECT add_to_package(389000, 'Ba Chỉ Bò Dày',                'Thịt nướng', 'ST03');
SELECT add_to_package(389000, 'Bắp Bò Hoa',                   'Thịt nướng', 'ST03');
SELECT add_to_package(389000, 'Gù Bò',                        'Thịt nướng', 'ST03');
SELECT add_to_package(389000, 'Lưỡi Bò',                      'Thịt nướng', 'ST03');
SELECT add_to_package(389000, 'Ba Chỉ Heo Tam Vị',            'Thịt nướng', 'ST03');
SELECT add_to_package(389000, 'Thăn Heo',                     'Thịt nướng', 'ST03');
SELECT add_to_package(389000, 'Ba Chỉ Heo Khổ Lớn',           'Thịt nướng', 'ST03');
SELECT add_to_package(389000, 'Lưỡi Heo',                     'Thịt nướng', 'ST03');
SELECT add_to_package(389000, 'Cốt Lết Heo',                  'Thịt nướng', 'ST03');
SELECT add_to_package(389000, 'Ba Chỉ Heo',                   'Thịt nướng', 'ST03');
SELECT add_to_package(389000, 'Nầm Heo',                      'Thịt nướng', 'ST03');
SELECT add_to_package(389000, 'Ba Chỉ Heo Mỏng',              'Thịt nướng', 'ST03');
SELECT add_to_package(389000, 'Nọng Heo',                     'Thịt nướng', 'ST03');
SELECT add_to_package(389000, 'Sườn Heo',                     'Thịt nướng', 'ST03');
SELECT add_to_package(389000, 'Cánh Gà',                      'Thịt nướng', 'ST03');
SELECT add_to_package(389000, 'Thịt gà Seseri',               'Thịt nướng', 'ST03');
SELECT add_to_package(389000, 'Thịt gà',                           'Thịt nướng', 'ST03');

-- 4. Hải sản nướng (ST03)
SELECT add_to_package(389000, 'Tôm',                          'Hải sản nướng', 'ST03');
SELECT add_to_package(389000, 'Mực',                          'Hải sản nướng', 'ST03');
SELECT add_to_package(389000, 'Bạch Tuộc',                    'Hải sản nướng', 'ST03');

-- 5. Sushi (ST04)
SELECT add_to_package(389000, 'Inari Cá Hồi Mayo',            'Sushi', 'ST04');
SELECT add_to_package(389000, 'Inari Cá Ngừ Mayo',            'Sushi', 'ST04');
SELECT add_to_package(389000, 'Inari Truyền Thống',           'Sushi', 'ST04');
SELECT add_to_package(389000, 'Inari Phô mai Nướng',           'Sushi', 'ST04');
SELECT add_to_package(389000, 'Nigiri Cá Hồi Mayo',           'Sushi', 'ST04');
SELECT add_to_package(389000, 'Nigiri Lươn',                  'Sushi', 'ST04');
SELECT add_to_package(389000, 'Nigiri Cá Hồi Nướng Trứng Tôm','Sushi', 'ST04');
SELECT add_to_package(389000, 'Nigiri Cá Hồi Nướng',          'Sushi', 'ST04');
SELECT add_to_package(389000, 'Nigiri Cá Hồi',                'Sushi', 'ST04');
SELECT add_to_package(389000, 'Nigiri Bạch Tuộc',             'Sushi', 'ST04');
SELECT add_to_package(389000, 'Nigiri Bò',                    'Sushi', 'ST04');
SELECT add_to_package(389000, 'Nigiri Bơ Cá Hồi',             'Sushi', 'ST04');
SELECT add_to_package(389000, 'Nigiri Cá Trích',              'Sushi', 'ST04');
SELECT add_to_package(389000, 'Nigiri Cá Ngừ Nướng',          'Sushi', 'ST04');
SELECT add_to_package(389000, 'Nigiri Cá Ngừ',                'Sushi', 'ST04');
SELECT add_to_package(389000, 'Nigiri Tôm',                   'Sushi', 'ST04');
SELECT add_to_package(389000, 'Nigiri Trứng',                 'Sushi', 'ST04');
SELECT add_to_package(389000, 'Nigiri Thanh Cua',             'Sushi', 'ST04');
SELECT add_to_package(389000, 'Sushi Cá Hồi',                 'Sushi', 'ST04');
SELECT add_to_package(389000, 'Sushi Lươn',                   'Sushi', 'ST04');
SELECT add_to_package(389000, 'Sushi Cá Hồi Nướng',           'Sushi', 'ST04');
SELECT add_to_package(389000, 'Sushi Chiên',                  'Sushi', 'ST04');
SELECT add_to_package(389000, 'Sushi Cá Hồi Nướng Phô mai',    'Sushi', 'ST04');
SELECT add_to_package(389000, 'Sushi Truyền Thống',           'Sushi', 'ST04');
SELECT add_to_package(389000, 'Sushi Trứng Tôm',              'Sushi', 'ST04');

-- 6. Sashimi (ST02) -> NHÓM MỚI CHỈ CÓ TỪ 389K
SELECT add_to_package(389000, 'Sashimi Cá Kiếm',              'Sashimi', 'ST02');
SELECT add_to_package(389000, 'Sashimi Cá Trích',             'Sashimi', 'ST02');
SELECT add_to_package(389000, 'Sashimi Cá Ngừ',               'Sashimi', 'ST02');
SELECT add_to_package(389000, 'Sashimi Cá Kiếm Khè Lửa',      'Sashimi', 'ST02');
SELECT add_to_package(389000, 'Sashimi Cá Hồi',               'Sashimi', 'ST02');
SELECT add_to_package(389000, 'Sashimi Bạch Tuộc',            'Sashimi', 'ST02');
SELECT add_to_package(389000, 'Sashimi Tổng Hợp',             'Sashimi', 'ST02');
SELECT add_to_package(389000, 'Trứng Cá Trứng',               'Sashimi', 'ST02');
SELECT add_to_package(389000, 'Cá Ngừ Đại Dương/Negi',        'Sashimi', 'ST02');

-- 7. Lẩu (ST05)
SELECT add_to_package(389000, 'Lẩu Hải Sản',                  'Lẩu', 'ST05');
SELECT add_to_package(389000, 'Lẩu Thịt Thập Cẩm',            'Lẩu', 'ST05');

-- 8. Cơm (ST05)
SELECT add_to_package(389000, 'Cơm Trộn Gyusachi',            'Cơm', 'ST05');
SELECT add_to_package(389000, 'Cơm Trộn Truyền Thống',        'Cơm', 'ST05');
SELECT add_to_package(389000, 'Cơm Trộn Cá Hồi',              'Cơm', 'ST05');
SELECT add_to_package(389000, 'Cơm Chiên Cá Hồi',             'Cơm', 'ST05');
SELECT add_to_package(389000, 'Cơm Chiên Hải Sản',            'Cơm', 'ST05');
SELECT add_to_package(389000, 'Cơm Chiên Trứng',              'Cơm', 'ST05');
SELECT add_to_package(389000, 'Cơm Chiên Bò',                 'Cơm', 'ST05');
SELECT add_to_package(389000, 'Cơm Thịt Bò Xào',              'Cơm', 'ST05');
SELECT add_to_package(389000, 'Cơm Thịt Bằm',                 'Cơm', 'ST05');

-- 9. Pizza (ST05)
SELECT add_to_package(389000, 'Pizza Ngô',                    'Pizza', 'ST05');
SELECT add_to_package(389000, 'Pizza Phô mai',                 'Pizza', 'ST05');
SELECT add_to_package(389000, 'Pizza Gyusachi',               'Pizza', 'ST05');

-- 10. Món ăn thêm (ST05)
SELECT add_to_package(389000, 'Khoai lang chiên',             'Món ăn thêm', 'ST05');
SELECT add_to_package(389000, 'Khoai lang lắc phô mai',        'Món ăn thêm', 'ST05');
SELECT add_to_package(389000, 'Da gà chiên',                  'Món ăn thêm', 'ST05');
SELECT add_to_package(389000, 'Cánh gà chiên',                'Món ăn thêm', 'ST05');
SELECT add_to_package(389000, 'Thịt heo xiên',                'Món ăn thêm', 'ST05');
SELECT add_to_package(389000, 'Gà chiên xù',                  'Món ăn thêm', 'ST05');
SELECT add_to_package(389000, 'Sụn Gà Chiên',                 'Món ăn thêm', 'ST05');
SELECT add_to_package(389000, 'Gà rán truyền thống',          'Món ăn thêm', 'ST05');
SELECT add_to_package(389000, 'Gà rán lắc phô mai',            'Món ăn thêm', 'ST05');
SELECT add_to_package(389000, 'Gà rán cay',                   'Món ăn thêm', 'ST05');
SELECT add_to_package(389000, 'Bánh xèo',                     'Món ăn thêm', 'ST05');
SELECT add_to_package(389000, 'Sủi Cảo Chiên',                'Món ăn thêm', 'ST05');
SELECT add_to_package(389000, 'Takoyaki',                     'Món ăn thêm', 'ST05');
SELECT add_to_package(389000, 'Khoai lang kén',               'Món ăn thêm', 'ST05');
SELECT add_to_package(389000, 'Há cảo chiên',                 'Món ăn thêm', 'ST05');
SELECT add_to_package(389000, 'Khoai tây chiên',              'Món ăn thêm', 'ST05');
SELECT add_to_package(389000, 'Khoai tây lắc phô mai',         'Món ăn thêm', 'ST05');
SELECT add_to_package(389000, 'Phô mai que',                   'Món ăn thêm', 'ST05');
SELECT add_to_package(389000, 'Gà sốt teriyaki',              'Món ăn thêm', 'ST05');

-- 11. Mỳ (ST05)
SELECT add_to_package(389000, 'Mì Lạnh Kim Chi',              'Mì', 'ST05');
SELECT add_to_package(389000, 'Mì Lạnh',                      'Mì', 'ST05');
SELECT add_to_package(389000, 'Mì Udon Miso',                 'Mì', 'ST05');
SELECT add_to_package(389000, 'Mì Udon Kimchi',              'Mì', 'ST05');
SELECT add_to_package(389000, 'Mì Udon Xào Kim Chi',          'Mì', 'ST05');
SELECT add_to_package(389000, 'Mì Xào Bò',                    'Mì', 'ST05');
SELECT add_to_package(389000, 'Mì Xào Hải Sản',               'Mì', 'ST05');
SELECT add_to_package(389000, 'Mì Udon Xào Bò',               'Mì', 'ST05');
SELECT add_to_package(389000, 'Mì Udon Xào Hải Sản',          'Mì', 'ST05');

-- 12. Soup (ST05)
SELECT add_to_package(389000, 'Soup Rong Biển',               'Soup', 'ST05');
SELECT add_to_package(389000, 'Soup Miso',                    'Soup', 'ST05');
SELECT add_to_package(389000, 'Soup Cay',                     'Soup', 'ST05');
SELECT add_to_package(389000, 'Soup Trứng',                   'Soup', 'ST05');

-- 13. Kim Chi (ST04)
SELECT add_to_package(389000, 'Kim Chi Dưa Leo',              'Kim chi', 'ST04');
SELECT add_to_package(389000, 'Kim Chi Cải Thảo',             'Kim chi', 'ST04');

-- ---------- C. Kiểm tra ----------

SELECT COUNT(*) AS so_mon_389k
FROM package_items
WHERE package_id = (SELECT id FROM packages WHERE price = 389000);

SELECT m.category, COUNT(*) AS so_mon
FROM package_items pi
JOIN menu_items m ON m.id = pi.menu_item_id
WHERE pi.package_id = (SELECT id FROM packages WHERE price = 389000)
GROUP BY m.category
ORDER BY CASE m.category
    WHEN 'Khai vị' THEN 1    WHEN 'Salad' THEN 2        WHEN 'Kim chi' THEN 3
    WHEN 'Thịt nướng' THEN 4 WHEN 'Hải sản nướng' THEN 5 WHEN 'Sashimi' THEN 6
    WHEN 'Sushi' THEN 7      WHEN 'Lẩu' THEN 8          WHEN 'Cơm' THEN 9
    WHEN 'Pizza' THEN 10     WHEN 'Mì' THEN 11          WHEN 'Món ăn thêm' THEN 12
    WHEN 'Soup' THEN 13      WHEN 'Topping' THEN 14     ELSE 15 END;