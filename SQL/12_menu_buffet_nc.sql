-- =====================================================
-- BUFFET THỨC UỐNG (49K, 69K, 139K)
-- 49K: áp dụng thứ 2 - thứ 5 | 69K: thứ 6, thứ 7, chủ nhật
-- Trạm pha chế: ST01
-- =====================================================

-- ---------- 1. TẠO CÁC GÓI BUFFET NƯỚC ----------
INSERT INTO packages (price, name) VALUES (49000, 'Buffet Nước 49K (T2 - T5)') ON CONFLICT DO NOTHING;
INSERT INTO packages (price, name) VALUES (69000, 'Buffet Nước 69K (T6 - CN)') ON CONFLICT DO NOTHING;
INSERT INTO packages (price, name) VALUES (139000, 'Buffet Rượu & Bia 139K') ON CONFLICT DO NOTHING;

-- Ngày áp dụng của từng gói (số thứ trong tuần kiểu ISO: 1=Thứ 2 ... 7=Chủ nhật)
-- Dùng để app tự gợi ý gói nước đúng theo ngày: EXTRACT(ISODOW FROM NOW())
ALTER TABLE packages ADD COLUMN IF NOT EXISTS valid_days VARCHAR(20);
UPDATE packages SET valid_days = '1,2,3,4'         WHERE price = 49000;
UPDATE packages SET valid_days = '5,6,7'           WHERE price = 69000;
UPDATE packages SET valid_days = '1,2,3,4,5,6,7'   WHERE price = 139000;

-- ---------- 2. THÊM MÓN CHO GÓI 69K ----------
-- SODA (ST01)
SELECT add_to_package(69000, 'Soda Chanh',               'Thức uống', 'ST01');
SELECT add_to_package(69000, 'Soda Đào',                 'Thức uống', 'ST01');
SELECT add_to_package(69000, 'Soda Chanh Dây',           'Thức uống', 'ST01');
SELECT add_to_package(69000, 'Soda Dưa Lưới',            'Thức uống', 'ST01');
SELECT add_to_package(69000, 'Soda Việt Quất',           'Thức uống', 'ST01');
SELECT add_to_package(69000, 'Soda Vải',                 'Thức uống', 'ST01');
SELECT add_to_package(69000, 'Soda Bưởi',                'Thức uống', 'ST01');
SELECT add_to_package(69000, 'Soda Lựu',                 'Thức uống', 'ST01');
SELECT add_to_package(69000, 'Soda Xoài',                'Thức uống', 'ST01');
SELECT add_to_package(69000, 'Soda Nho',                 'Thức uống', 'ST01');

-- NƯỚC TRÁI CÂY (ST01)
SELECT add_to_package(69000, 'Nước Cam',                 'Thức uống', 'ST01');
SELECT add_to_package(69000, 'Nước Táo',                 'Thức uống', 'ST01');

-- TRÀ (ST01)
SELECT add_to_package(69000, 'Trà Olong',                'Thức uống', 'ST01');
SELECT add_to_package(69000, 'Trà Lipton',               'Thức uống', 'ST01');
SELECT add_to_package(69000, 'Trà Nhài',                 'Thức uống', 'ST01');
SELECT add_to_package(69000, 'Trà Gừng',                 'Thức uống', 'ST01');

-- NƯỚC NGỌT (ST01)
SELECT add_to_package(69000, 'Pepsi',                    'Thức uống', 'ST01');
SELECT add_to_package(69000, 'Pepsi Lemon',              'Thức uống', 'ST01');
SELECT add_to_package(69000, '7 Up',                     'Thức uống', 'ST01');
SELECT add_to_package(69000, 'Soda Không Đường',         'Thức uống', 'ST01');
SELECT add_to_package(69000, 'Sprite',                   'Thức uống', 'ST01');
SELECT add_to_package(69000, 'Cocacola',                 'Thức uống', 'ST01');
SELECT add_to_package(69000, 'Aquafina',                 'Thức uống', 'ST01');

-- ---------- 3. COPY MÓN CHO GÓI 49K (Giống hệt 69K) ----------
INSERT INTO package_items (package_id, menu_item_id)
SELECT (SELECT id FROM packages WHERE price = 49000), menu_item_id
FROM package_items
WHERE package_id = (SELECT id FROM packages WHERE price = 69000)
ON CONFLICT DO NOTHING;


-- ---------- 4. GÓI BUFFET RƯỢU & BIA 139K ----------
-- 4.1 Copy toàn bộ nước từ gói 69K sang gói 139K
INSERT INTO package_items (package_id, menu_item_id)
SELECT (SELECT id FROM packages WHERE price = 139000), menu_item_id
FROM package_items
WHERE package_id = (SELECT id FROM packages WHERE price = 69000)
ON CONFLICT DO NOTHING;

-- 4.2 Thêm các món Cocktail, Rượu, Bia riêng của 139K (ST01)
-- COCKTAIL (ST01)
SELECT add_to_package(139000, 'Cocktail Chanh',           'Thức uống', 'ST01');
SELECT add_to_package(139000, 'Cocktail Đào',             'Thức uống', 'ST01');
SELECT add_to_package(139000, 'Cocktail Chanh Dây',       'Thức uống', 'ST01');
SELECT add_to_package(139000, 'Cocktail Dưa Lưới',        'Thức uống', 'ST01');
SELECT add_to_package(139000, 'Cocktail Việt Quất',       'Thức uống', 'ST01');
SELECT add_to_package(139000, 'Cocktail Vải',             'Thức uống', 'ST01');
SELECT add_to_package(139000, 'Cocktail Bưởi',            'Thức uống', 'ST01');
SELECT add_to_package(139000, 'Cocktail Lựu',             'Thức uống', 'ST01');
SELECT add_to_package(139000, 'Cocktail Xoài',            'Thức uống', 'ST01');
SELECT add_to_package(139000, 'Cocktail Nho',             'Thức uống', 'ST01');

-- RƯỢU / WINE (ST01)
SELECT add_to_package(139000, 'Rượu Nho & Cam',           'Thức uống', 'ST01');
SELECT add_to_package(139000, 'Soju',                     'Thức uống', 'ST01');
SELECT add_to_package(139000, 'Ume Shyu (Mơ)',            'Thức uống', 'ST01');
SELECT add_to_package(139000, 'Haiball',                  'Thức uống', 'ST01');
SELECT add_to_package(139000, 'Coca Haiball',             'Thức uống', 'ST01');

-- BIA / BEER (ST01)
SELECT add_to_package(139000, 'Tiger Beer',               'Thức uống', 'ST01');
SELECT add_to_package(139000, 'Heineken Beer',            'Thức uống', 'ST01');


-- ---------- 5. Kiểm tra ----------
-- Phải thấy: 49K = 23 món, 69K = 23 món, 139K = 40 món
SELECT p.name, p.valid_days, COUNT(pi.menu_item_id) AS so_mon
FROM packages p
LEFT JOIN package_items pi ON pi.package_id = p.id
WHERE p.price IN (49000, 69000, 139000)
GROUP BY p.name, p.valid_days, p.price
ORDER BY p.price;
