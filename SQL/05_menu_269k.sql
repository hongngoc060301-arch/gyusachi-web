-- =====================================================
-- 05. MENU BUFFET 269K  (đầy đủ)
-- Chạy SAU file 04. Chạy lại nhiều lần cũng không bị trùng.
--
-- Quy tắc: gói 269K gồm TOÀN BỘ món gói 199K + các món riêng bên dưới.
-- Mã trạm: ST01 pha chế | ST02 sashimi | ST03 thịt nướng
--          ST04 khai vị / salad / kim chi / sushi | ST05 bếp nóng
-- Thứ tự: Khai vị > Salad > Kim chi > Thịt nướng > Sushi
--         > Cơm > Mì > Món ăn thêm > Soup > Topping
-- =====================================================


-- ---------- A. Đồng bộ các món gói 199K đã nhập ----------

-- Khai vị, Salad, Kim chi: ST04
UPDATE menu_items SET station_id = 'ST04'
WHERE category IN ('Khai vị', 'Salad', 'Kim chi');

-- Tên đúng theo menu 269K
UPDATE menu_items SET name = 'Dồi sụn'
WHERE name = 'Dải sụn'
  AND NOT EXISTS (SELECT 1 FROM menu_items WHERE name = 'Dồi sụn');

UPDATE menu_items SET name = 'Nigiri trứng'
WHERE name = 'Sushi trứng'
  AND NOT EXISTS (SELECT 1 FROM menu_items WHERE name = 'Nigiri trứng');

UPDATE menu_items SET name = 'Nigiri cá ngừ'
WHERE name = 'Sushi cá ngừ'
  AND NOT EXISTS (SELECT 1 FROM menu_items WHERE name = 'Nigiri cá ngừ');

UPDATE menu_items SET name = 'Nigiri thanh cua'
WHERE name = 'Sushi thanh cua'
  AND NOT EXISTS (SELECT 1 FROM menu_items WHERE name = 'Nigiri thanh cua');

-- Tách nhóm "Cơm / Soup" thành "Soup" và "Cơm"
UPDATE menu_items SET category = 'Soup'
WHERE category = 'Cơm / Soup' AND name LIKE 'Soup%';

UPDATE menu_items SET category = 'Cơm'
WHERE category = 'Cơm / Soup';


-- ---------- B. Copy toàn bộ món gói 199K sang gói 269K ----------

INSERT INTO package_items (package_id, menu_item_id)
SELECT (SELECT id FROM packages WHERE price = 269000), menu_item_id
FROM package_items
WHERE package_id = (SELECT id FROM packages WHERE price = 199000)
ON CONFLICT DO NOTHING;


-- ---------- C. Món RIÊNG của 269K (đã bỏ món trùng 199K) ----------

-- 1. Khai vị
SELECT add_to_package(269000, 'Da cá hồi chiên',          'Khai vị', 'ST04');

-- 2. Salad
SELECT add_to_package(269000, 'Salad gà',                 'Salad', 'ST04');

-- 3. Kim chi (269K không có món riêng)

-- 4. Thịt nướng
SELECT add_to_package(269000, 'Set thịt tổng hợp 5 loại', 'Thịt nướng', 'ST03');
SELECT add_to_package(269000, 'Ba chỉ bò Mỹ',             'Thịt nướng', 'ST03');
SELECT add_to_package(269000, 'Bắp bò hoa',               'Thịt nướng', 'ST03');
SELECT add_to_package(269000, 'Ba chỉ bò nấm đùi gà',     'Thịt nướng', 'ST03');
SELECT add_to_package(269000, 'Ba chỉ heo tam vị',        'Thịt nướng', 'ST03');
SELECT add_to_package(269000, 'Ba chỉ heo nấm kim châm',  'Thịt nướng', 'ST03');
SELECT add_to_package(269000, 'Ba chỉ heo khổ lớn',       'Thịt nướng', 'ST03');
SELECT add_to_package(269000, 'Cốt lết heo',              'Thịt nướng', 'ST03');
SELECT add_to_package(269000, 'Nọng heo',                 'Thịt nướng', 'ST03');
SELECT add_to_package(269000, 'Bắp nướng bơ',             'Thịt nướng', 'ST03');

-- 5. Sushi
SELECT add_to_package(269000, 'Sushi cá hồi nướng',       'Sushi', 'ST04');
SELECT add_to_package(269000, 'Nigiri cá ngừ nướng',      'Sushi', 'ST04');
SELECT add_to_package(269000, 'Nigiri bò',                'Sushi', 'ST04');

-- 6. Cơm
SELECT add_to_package(269000, 'Cơm trộn truyền thống',    'Cơm', 'ST05');
SELECT add_to_package(269000, 'Cơm trộn Gyusachi',        'Cơm', 'ST05');
SELECT add_to_package(269000, 'Cơm chiên cá hồi',         'Cơm', 'ST05');
SELECT add_to_package(269000, 'Cơm trộn cá hồi',          'Cơm', 'ST05');
SELECT add_to_package(269000, 'Cơm thịt bò xào',          'Cơm', 'ST05');
SELECT add_to_package(269000, 'Cơm thịt bằm',             'Cơm', 'ST05');

-- 7. Mì
SELECT add_to_package(269000, 'Mì lạnh',                  'Mì', 'ST05');
SELECT add_to_package(269000, 'Mì udon miso',             'Mì', 'ST05');
SELECT add_to_package(269000, 'Mì udon kimchi',           'Mì', 'ST05');
SELECT add_to_package(269000, 'Mì xào bò',                'Mì', 'ST05');
SELECT add_to_package(269000, 'Mì xào hải sản',           'Mì', 'ST05');

-- 8. Món ăn thêm
SELECT add_to_package(269000, 'Cánh gà chiên',            'Món ăn thêm', 'ST05');
SELECT add_to_package(269000, 'Thịt heo xiên',            'Món ăn thêm', 'ST05');
SELECT add_to_package(269000, 'Gà chiên xù',              'Món ăn thêm', 'ST05');
SELECT add_to_package(269000, 'Gà rán lắc phô mai',       'Món ăn thêm', 'ST05');
SELECT add_to_package(269000, 'Bánh xèo',                 'Món ăn thêm', 'ST05');
SELECT add_to_package(269000, 'Sủi cảo chiên',            'Món ăn thêm', 'ST05');
SELECT add_to_package(269000, 'Gà sốt teriyaki',          'Món ăn thêm', 'ST05');

-- 9. Soup
SELECT add_to_package(269000, 'Soup trứng',               'Soup', 'ST05');

-- 10. Topping
SELECT add_to_package(269000, 'Sốt Bonya củ cải',         'Topping', 'ST05');
SELECT add_to_package(269000, 'Hành paro muối',           'Topping', 'ST05');
SELECT add_to_package(269000, 'Bí ngô',                   'Topping', 'ST05');
SELECT add_to_package(269000, 'Hành tây nướng',           'Topping', 'ST05');
SELECT add_to_package(269000, 'Khoai lang',               'Topping', 'ST05');
SELECT add_to_package(269000, 'Thanh cua',                'Topping', 'ST05');
SELECT add_to_package(269000, 'Nấm đùi gà',               'Topping', 'ST05');
SELECT add_to_package(269000, 'Trứng',                    'Topping', 'ST05');


-- ---------- D. Kiểm tra ----------

-- Tổng phải là 94 món (52 món của 199K + 42 món riêng)
SELECT COUNT(*) AS so_mon_269k
FROM package_items
WHERE package_id = (SELECT id FROM packages WHERE price = 269000);

-- Số món theo từng nhóm
SELECT m.category, COUNT(*) AS so_mon
FROM package_items pi
JOIN menu_items m ON m.id = pi.menu_item_id
WHERE pi.package_id = (SELECT id FROM packages WHERE price = 269000)
GROUP BY m.category
ORDER BY CASE m.category
    WHEN 'Khai vị' THEN 1  WHEN 'Salad' THEN 2   WHEN 'Kim chi' THEN 3
    WHEN 'Thịt nướng' THEN 4 WHEN 'Sushi' THEN 5 WHEN 'Cơm' THEN 6
    WHEN 'Mì' THEN 7 WHEN 'Món ăn thêm' THEN 8   WHEN 'Soup' THEN 9
    WHEN 'Topping' THEN 10 ELSE 11 END;
