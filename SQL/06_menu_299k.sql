-- =====================================================
-- 06. MENU BUFFET 299K  (đầy đủ)
-- Chạy SAU file 05 (gói 269K phải có sẵn 94 món).
-- Chạy lại nhiều lần cũng không bị trùng.
--
-- Quy tắc: gói 299K gồm TOÀN BỘ món gói 269K (đã gồm 199K) + món riêng bên dưới.
-- Mã trạm: ST01 pha chế | ST02 sashimi | ST03 thịt nướng
--          ST04 khai vị / salad / kim chi / sushi | ST05 bếp nóng
-- Thứ tự: Khai vị > Salad > Kim chi > Thịt nướng > Sushi > Lẩu
--         > Cơm > Pizza > Mì > Món ăn thêm > Soup > Topping
-- =====================================================


-- ---------- A. Đồng bộ tên món ----------

-- Menu 299K ghi "Salad Thanh Cua"
UPDATE menu_items SET name = 'Salad thanh cua'
WHERE name = 'Salad cua'
  AND NOT EXISTS (SELECT 1 FROM menu_items WHERE name = 'Salad thanh cua');


-- ---------- B. Copy toàn bộ món gói 269K sang gói 299K ----------

INSERT INTO package_items (package_id, menu_item_id)
SELECT (SELECT id FROM packages WHERE price = 299000), menu_item_id
FROM package_items
WHERE package_id = (SELECT id FROM packages WHERE price = 269000)
ON CONFLICT DO NOTHING;


-- ---------- C. Món RIÊNG của 299K (đã bỏ món trùng 199K / 269K) ----------

-- 1. Khai vị (299K không có món riêng)

-- 2. Salad
SELECT add_to_package(299000, 'Salad hải sản',                'Salad', 'ST04');

-- 3. Kim chi (299K không có món riêng)

-- 4. Thịt nướng
SELECT add_to_package(299000, 'Gyusachi karubi',              'Thịt nướng', 'ST03');
SELECT add_to_package(299000, 'Gù bò',                        'Thịt nướng', 'ST03');
SELECT add_to_package(299000, 'Gầu bò',                       'Thịt nướng', 'ST03');
SELECT add_to_package(299000, 'Ba chỉ bò cuốn đậu bắp',       'Thịt nướng', 'ST03');
SELECT add_to_package(299000, 'Ba chỉ heo mỏng',              'Thịt nướng', 'ST03');
SELECT add_to_package(299000, 'Nầm heo',                      'Thịt nướng', 'ST03');

-- 5. Sushi
SELECT add_to_package(299000, 'Nigiri bạch tuộc',             'Sushi', 'ST04');
SELECT add_to_package(299000, 'Nigiri cá trích',              'Sushi', 'ST04');
SELECT add_to_package(299000, 'Nigiri bơ cá hồi',             'Sushi', 'ST04');
SELECT add_to_package(299000, 'Sushi cá hồi nướng phô mai',   'Sushi', 'ST04');

-- 6. Lẩu
SELECT add_to_package(299000, 'Lẩu thịt thập cẩm',            'Lẩu', 'ST05');
SELECT add_to_package(299000, 'Mì tôm',                       'Lẩu', 'ST05');
SELECT add_to_package(299000, 'Mì nhật',                      'Lẩu', 'ST05');
SELECT add_to_package(299000, 'Mì udon',                      'Lẩu', 'ST05');

-- 7. Cơm
SELECT add_to_package(299000, 'Cơm chiên trứng',              'Cơm', 'ST05');
SELECT add_to_package(299000, 'Cơm chiên bò',                 'Cơm', 'ST05');

-- 8. Pizza
SELECT add_to_package(299000, 'Pizza ngô',                    'Pizza', 'ST05');
SELECT add_to_package(299000, 'Pizza phô mai',                'Pizza', 'ST05');
SELECT add_to_package(299000, 'Pizza Gyusachi',               'Pizza', 'ST05');

-- 9. Mì
SELECT add_to_package(299000, 'Mì udon xào kim chi',          'Mì', 'ST05');
SELECT add_to_package(299000, 'Mì udon xào bò',               'Mì', 'ST05');
SELECT add_to_package(299000, 'Mì udon xào hải sản',          'Mì', 'ST05');

-- 10. Món ăn thêm (299K không có món riêng)
-- 11. Soup (299K không có món riêng)
-- 12. Topping (299K không có món riêng)


-- ---------- D. Kiểm tra ----------

-- Tổng phải là 117 món (94 món của 269K + 23 món riêng)
SELECT COUNT(*) AS so_mon_299k
FROM package_items
WHERE package_id = (SELECT id FROM packages WHERE price = 299000);

-- Số món theo từng nhóm
SELECT m.category, COUNT(*) AS so_mon
FROM package_items pi
JOIN menu_items m ON m.id = pi.menu_item_id
WHERE pi.package_id = (SELECT id FROM packages WHERE price = 299000)
GROUP BY m.category
ORDER BY CASE m.category
    WHEN 'Khai vị' THEN 1    WHEN 'Salad' THEN 2   WHEN 'Kim chi' THEN 3
    WHEN 'Thịt nướng' THEN 4 WHEN 'Sushi' THEN 5   WHEN 'Lẩu' THEN 6
    WHEN 'Cơm' THEN 7        WHEN 'Pizza' THEN 8   WHEN 'Mì' THEN 9
    WHEN 'Món ăn thêm' THEN 10 WHEN 'Soup' THEN 11 WHEN 'Topping' THEN 12
    ELSE 13 END;
