-- =====================================================
-- 04. MENU BUFFET 199K
-- Chạy SAU file 03.
-- Mã trạm: ST01 pha chế | ST02 sashimi | ST03 thịt nướng
--          ST04 sushi   | ST05 bếp nóng
-- =====================================================

-- Khai vị
SELECT add_to_package(199000, 'Dưa leo tổng hợp',        'Khai vị', 'ST04');
SELECT add_to_package(199000, 'Đậu nành Nhật',           'Khai vị', 'ST04');
SELECT add_to_package(199000, 'Đậu phộng rang muối',     'Khai vị', 'ST04');
SELECT add_to_package(199000, 'Trứng cút ngâm',          'Khai vị', 'ST04');
SELECT add_to_package(199000, 'Lá rong biển',            'Khai vị', 'ST04');
SELECT add_to_package(199000, 'Dưa trộn',                'Khai vị', 'ST04');

-- Salad
SELECT add_to_package(199000, 'Salad truyền thống',      'Salad', 'ST04');
SELECT add_to_package(199000, 'Salad hành',              'Salad', 'ST04');
SELECT add_to_package(199000, 'Salad rong biển',         'Salad', 'ST04');
SELECT add_to_package(199000, 'Salad da cá hồi chiên',   'Salad', 'ST04');
SELECT add_to_package(199000, 'Salad cua',               'Salad', 'ST04');
SELECT add_to_package(199000, 'Gyusachi salad',          'Salad', 'ST04');

-- Kim chi
SELECT add_to_package(199000, 'Kim chi dưa leo',         'Kim chi', 'ST04');
SELECT add_to_package(199000, 'Kim chi củ cải',          'Kim chi', 'ST04');
SELECT add_to_package(199000, 'Kim chi cải thảo',        'Kim chi', 'ST04');

-- Thịt nướng
SELECT add_to_package(199000, 'Thăn heo',                'Thịt nướng', 'ST03');
SELECT add_to_package(199000, 'Ba chỉ bò',               'Thịt nướng', 'ST03');
SELECT add_to_package(199000, 'Ba chỉ bò mỏng',          'Thịt nướng', 'ST03');
SELECT add_to_package(199000, 'Ba chỉ bò dày',           'Thịt nướng', 'ST03');
SELECT add_to_package(199000, 'Ba chỉ bò nấm kim châm',  'Thịt nướng', 'ST03');
SELECT add_to_package(199000, 'Thăn ngoại bò',           'Thịt nướng', 'ST03');
SELECT add_to_package(199000, 'Ba chỉ heo',              'Thịt nướng', 'ST03');
SELECT add_to_package(199000, 'Sườn heo',                'Thịt nướng', 'ST03');
SELECT add_to_package(199000, 'Lưỡi heo',                'Thịt nướng', 'ST03');
SELECT add_to_package(199000, 'Diềm heo',                'Thịt nướng', 'ST03');
SELECT add_to_package(199000, 'Thịt gà',                 'Thịt nướng', 'ST03');
SELECT add_to_package(199000, 'Dải sụn',                 'Thịt nướng', 'ST03');
SELECT add_to_package(199000, 'Cánh gà',                 'Thịt nướng', 'ST03');
SELECT add_to_package(199000, 'Xúc xích',                'Thịt nướng', 'ST03');

-- Sushi
SELECT add_to_package(199000, 'Sushi cá hồi',            'Sushi', 'ST04');
SELECT add_to_package(199000, 'Sushi chiên',             'Sushi', 'ST04');
SELECT add_to_package(199000, 'Sushi truyền thống',      'Sushi', 'ST04');
SELECT add_to_package(199000, 'Sushi trứng',             'Sushi', 'ST04');
SELECT add_to_package(199000, 'Sushi cá ngừ',            'Sushi', 'ST04');
SELECT add_to_package(199000, 'Sushi thanh cua',         'Sushi', 'ST04');

-- Món ăn thêm
SELECT add_to_package(199000, 'Takoyaki',                'Món ăn thêm', 'ST05');
SELECT add_to_package(199000, 'Gà rán truyền thống',     'Món ăn thêm', 'ST05');
SELECT add_to_package(199000, 'Khoai tây chiên',         'Món ăn thêm', 'ST05');
SELECT add_to_package(199000, 'Khoai tây lắc phô mai',   'Món ăn thêm', 'ST05');
SELECT add_to_package(199000, 'Há cảo chiên',            'Món ăn thêm', 'ST05');
SELECT add_to_package(199000, 'Khoai lang kén',          'Món ăn thêm', 'ST05');
SELECT add_to_package(199000, 'Phô mai que',             'Món ăn thêm', 'ST05');
SELECT add_to_package(199000, 'Phô mai viên',            'Món ăn thêm', 'ST05');

-- Cơm / Soup
SELECT add_to_package(199000, 'Cơm trộn rong biển',      'Cơm / Soup', 'ST05');
SELECT add_to_package(199000, 'Cơm chiên hải sản',       'Cơm / Soup', 'ST05');
SELECT add_to_package(199000, 'Soup cay',                'Cơm / Soup', 'ST05');
SELECT add_to_package(199000, 'Soup miso',               'Cơm / Soup', 'ST05');
SELECT add_to_package(199000, 'Soup rong biển',          'Cơm / Soup', 'ST05');

-- Topping
SELECT add_to_package(199000, 'Cơm trắng',               'Topping', 'ST05');
SELECT add_to_package(199000, 'Rau cuốn',                'Topping', 'ST05');
SELECT add_to_package(199000, 'Bắp ngô',                 'Topping', 'ST05');

-- Tráng miệng
SELECT add_to_package(199000, 'Kem/Dưa hấu',   'Tráng miệng', 'ST01');


-- Kiểm tra: gói 199K phải có 52 món
SELECT COUNT(*) AS so_mon
FROM package_items
WHERE package_id = (SELECT id FROM packages WHERE price = 199000);
