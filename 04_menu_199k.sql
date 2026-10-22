-- =====================================================
-- 04. MENU BUFFET 219K (theo menu mới)
-- Chạy SAU file 03.
-- Mã trạm: ST01 pha chế | ST02 sashimi | ST03 thịt nướng
--          ST04 sushi   | ST05 bếp nóng
-- =====================================================

-- Khai vị
SELECT add_to_package(219000, 'Dưa Leo Tổng Hợp',                'Khai vị',      'ST05');
SELECT add_to_package(219000, 'Đậu Nành Nhật',                   'Khai vị',      'ST05');
SELECT add_to_package(219000, 'Đậu Phộng Rang Muối',             'Khai vị',      'ST05');
SELECT add_to_package(219000, 'Trứng Cút Ngâm',                  'Khai vị',      'ST05');
SELECT add_to_package(219000, 'Lá Rong Biển',                    'Khai vị',      'ST05');
SELECT add_to_package(219000, 'Dưa Trộn',                        'Khai vị',      'ST05');

-- Salad
SELECT add_to_package(219000, 'Salad Truyền Thống',              'Salad',        'ST05');
SELECT add_to_package(219000, 'Salad Hành',                      'Salad',        'ST05');
SELECT add_to_package(219000, 'Salad Rong Biển',                 'Salad',        'ST05');
SELECT add_to_package(219000, 'Salad Da Cá Hồi Chiên',           'Salad',        'ST05');
SELECT add_to_package(219000, 'Salad Thanh Cua',                 'Salad',        'ST05');
SELECT add_to_package(219000, 'Gyusachi Salad',                  'Salad',        'ST05');

-- Kim chi
SELECT add_to_package(219000, 'Kim chi dưa leo',                 'Kim chi',      'ST05');
SELECT add_to_package(219000, 'Kim chi củ cải',                  'Kim chi',      'ST05');
SELECT add_to_package(219000, 'Kim chi cải thảo',                'Kim chi',      'ST05');

-- Thịt nướng
SELECT add_to_package(219000, 'Ba Chỉ Bò Mỏng',                  'Thịt nướng',   'ST03');
SELECT add_to_package(219000, 'Ba Chỉ Bò Mỹ',                    'Thịt nướng',   'ST03');
SELECT add_to_package(219000, 'Ba Chỉ Bò Dày',                   'Thịt nướng',   'ST03');
SELECT add_to_package(219000, 'Ba Chỉ Bò Nấm Kim Châm',          'Thịt nướng',   'ST03');
SELECT add_to_package(219000, 'Gù Bò',                           'Thịt nướng',   'ST03');
SELECT add_to_package(219000, 'Ba Chỉ Heo',                      'Thịt nướng',   'ST03');
SELECT add_to_package(219000, 'Ba Chỉ Heo Khổ Lớn',              'Thịt nướng',   'ST03');
SELECT add_to_package(219000, 'Sườn Heo',                        'Thịt nướng',   'ST03');
SELECT add_to_package(219000, 'Thăn Heo',                        'Thịt nướng',   'ST03');
SELECT add_to_package(219000, 'Lưỡi Heo',                        'Thịt nướng',   'ST03');
SELECT add_to_package(219000, 'Cánh Gà',                         'Thịt nướng',   'ST03');
SELECT add_to_package(219000, 'Thịt gà',                         'Thịt nướng',   'ST03');
SELECT add_to_package(219000, 'Xúc Xích',                        'Thịt nướng',   'ST03');
SELECT add_to_package(219000, 'Dồi Sụn',                         'Thịt nướng',   'ST03');

-- Sushi
SELECT add_to_package(219000, 'Sushi Cá Hồi',                    'Sushi',        'ST04');
SELECT add_to_package(219000, 'Sushi Chiên',                     'Sushi',        'ST04');
SELECT add_to_package(219000, 'Sushi Truyền Thống',              'Sushi',        'ST04');
SELECT add_to_package(219000, 'Nigiri Trứng',                    'Sushi',        'ST04');
SELECT add_to_package(219000, 'Nigiri Cá Ngừ',                   'Sushi',        'ST04');
SELECT add_to_package(219000, 'Nigiri Thanh Cua',                'Sushi',        'ST04');

-- Món ăn thêm
SELECT add_to_package(219000, 'Takoyaki',                        'Món ăn thêm',  'ST05');
SELECT add_to_package(219000, 'Gà rán truyền thống',             'Món ăn thêm',  'ST05');
SELECT add_to_package(219000, 'Khoai tây chiên',                 'Món ăn thêm',  'ST05');
SELECT add_to_package(219000, 'Khoai tây lắc phô mai',           'Món ăn thêm',  'ST05');
SELECT add_to_package(219000, 'Sủi Cảo Chiên',                   'Món ăn thêm',  'ST05');
SELECT add_to_package(219000, 'Khoai lang kén',                  'Món ăn thêm',  'ST05');
SELECT add_to_package(219000, 'Há cảo chiên',                    'Món ăn thêm',  'ST05');
SELECT add_to_package(219000, 'Phô mai que',                     'Món ăn thêm',  'ST05');

-- Cơm / Soup
SELECT add_to_package(219000, 'Cơm trộn rong biển',              'Cơm / Soup',   'ST05');
SELECT add_to_package(219000, 'Cơm chiên hải sản',               'Cơm / Soup',   'ST05');
SELECT add_to_package(219000, 'Soup cay',                        'Cơm / Soup',   'ST05');
SELECT add_to_package(219000, 'Soup miso',                       'Cơm / Soup',   'ST05');
SELECT add_to_package(219000, 'Soup rong biển',                  'Cơm / Soup',   'ST05');

-- Topping
SELECT add_to_package(219000, 'Cơm trắng',                       'Topping',      'ST05');
SELECT add_to_package(219000, 'Rau Cuộn',                        'Topping',      'ST05');
SELECT add_to_package(219000, 'Bắp ngô',                         'Topping',      'ST05');

-- Tráng miệng
SELECT add_to_package(219000, 'Kem / Dưa hấu',                   'Tráng miệng',  'ST01');


-- Kiểm tra: gói 219K phải có 52 món
SELECT COUNT(*) AS so_mon
FROM package_items
WHERE package_id = (SELECT id FROM packages WHERE price = 219000);
