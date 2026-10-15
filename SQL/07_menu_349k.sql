-- =====================================================
-- 07. MENU BUFFET 349K  (đầy đủ)
-- Chạy SAU file 06 (gói 299K phải có sẵn 117 món).
-- Chạy lại nhiều lần cũng không bị trùng.
--
-- Quy tắc: gói 349K gồm TOÀN BỘ món gói 299K (đã gồm 269K và 199K) + món riêng bên dưới.
-- Mã trạm: ST01 pha chế | ST02 sashimi | ST03 thịt nướng
--          ST04 khai vị / salad / kim chi / sushi | ST05 bếp nóng
-- Thứ tự: Khai vị > Salad > Kim chi > Thịt nướng > Hải sản nướng > Sushi
--         > Lẩu > Cơm > Pizza > Mì > Món ăn thêm > Soup > Topping
-- =====================================================


-- ---------- A. Copy toàn bộ món gói 299K sang gói 349K ----------

INSERT INTO package_items (package_id, menu_item_id)
SELECT (SELECT id FROM packages WHERE price = 349000), menu_item_id
FROM package_items
WHERE package_id = (SELECT id FROM packages WHERE price = 299000)
ON CONFLICT DO NOTHING;


-- ---------- B. Món RIÊNG của 349K (đã bỏ món trùng 199K / 269K / 299K) ----------

-- 1. Khai vị (349K không có món riêng)

-- 2. Salad
SELECT add_to_package(349000, 'Salad cá hồi',                 'Salad', 'ST04');

-- 3. Kim chi (349K không có món riêng)

-- 4. Thịt nướng
SELECT add_to_package(349000, 'Sườn bò',                      'Thịt nướng', 'ST03');
SELECT add_to_package(349000, 'Dẻ sườn bò',                   'Thịt nướng', 'ST03');
SELECT add_to_package(349000, 'Nạc cổ bò',                    'Thịt nướng', 'ST03');
SELECT add_to_package(349000, 'Ba chỉ bò cuộn măng tây',      'Thịt nướng', 'ST03');
SELECT add_to_package(349000, 'Thịt gà seseri',               'Thịt nướng', 'ST03');
SELECT add_to_package(349000, 'Phô mai nướng giấy bạc',       'Thịt nướng', 'ST03');

-- 5. Hải sản nướng (nhóm mới)
SELECT add_to_package(349000, 'Tôm',                          'Hải sản nướng', 'ST03');
SELECT add_to_package(349000, 'Mực',                          'Hải sản nướng', 'ST03');
SELECT add_to_package(349000, 'Bạch tuộc',                    'Hải sản nướng', 'ST03');

-- 6. Sushi
SELECT add_to_package(349000, 'Inari cá hồi mayo',            'Sushi', 'ST04');
SELECT add_to_package(349000, 'Inari cá ngừ mayo',            'Sushi', 'ST04');
SELECT add_to_package(349000, 'Inari truyền thống',           'Sushi', 'ST04');
SELECT add_to_package(349000, 'Inari phô mai nướng',          'Sushi', 'ST04');
SELECT add_to_package(349000, 'Nigiri cá hồi',                'Sushi', 'ST04');
SELECT add_to_package(349000, 'Nigiri cá hồi nướng',          'Sushi', 'ST04');
SELECT add_to_package(349000, 'Nigiri cá hồi mayo',           'Sushi', 'ST04');
SELECT add_to_package(349000, 'Sushi trứng tôm',              'Sushi', 'ST04');

-- 7. Lẩu
SELECT add_to_package(349000, 'Lẩu hải sản',                  'Lẩu', 'ST05');

-- 8. Cơm (349K không có món riêng)
-- 9. Pizza (349K không có món riêng)

-- 10. Mì
SELECT add_to_package(349000, 'Mì lạnh kim chi',              'Mì', 'ST05');

-- 11. Món ăn thêm
SELECT add_to_package(349000, 'Khoai lang chiên',             'Món ăn thêm', 'ST05');
SELECT add_to_package(349000, 'Khoai lang lắc phô mai',       'Món ăn thêm', 'ST05');
SELECT add_to_package(349000, 'Da gà chiên',                  'Món ăn thêm', 'ST05');
SELECT add_to_package(349000, 'Sụn gà chiên',                 'Món ăn thêm', 'ST05');
SELECT add_to_package(349000, 'Gà rán cay',                   'Món ăn thêm', 'ST05');

-- 12. Soup (349K không có món riêng)
-- 13. Topping (349K không có món riêng)


-- ---------- C. Kiểm tra ----------

-- Tổng phải là 142 món (117 món của 299K + 25 món riêng)
SELECT COUNT(*) AS so_mon_349k
FROM package_items
WHERE package_id = (SELECT id FROM packages WHERE price = 349000);

-- Số món theo từng nhóm
SELECT m.category, COUNT(*) AS so_mon
FROM package_items pi
JOIN menu_items m ON m.id = pi.menu_item_id
WHERE pi.package_id = (SELECT id FROM packages WHERE price = 349000)
GROUP BY m.category
ORDER BY CASE m.category
    WHEN 'Khai vị' THEN 1    WHEN 'Salad' THEN 2        WHEN 'Kim chi' THEN 3
    WHEN 'Thịt nướng' THEN 4 WHEN 'Hải sản nướng' THEN 5 WHEN 'Sushi' THEN 6
    WHEN 'Lẩu' THEN 7        WHEN 'Cơm' THEN 8          WHEN 'Pizza' THEN 9
    WHEN 'Mì' THEN 10        WHEN 'Món ăn thêm' THEN 11 WHEN 'Soup' THEN 12
    WHEN 'Topping' THEN 13   ELSE 14 END;
