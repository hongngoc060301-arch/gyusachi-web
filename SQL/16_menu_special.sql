-- =====================================================
-- 16. SPECIAL MENU (áp dụng menu 349K - 389K - 469K)
-- Chạy SAU file 14. Chạy lại nhiều lần không bị trùng.
--
-- Món mới -> nhóm 'Special'. Món topping đã có sẵn (Nấm kim châm, Đậu bắp...)
-- thì dùng lại, chỉ gắn thêm vào gói 349K / 389K / 469K.
-- Mã trạm: ST03 thịt nướng | ST05 bếp nóng
-- =====================================================

CREATE TEMP TABLE sp (name TEXT, cat TEXT, station TEXT);

INSERT INTO sp (name, cat, station) VALUES
-- Sốt tỏi garlic (nướng)
('Gyusachi karubi sốt tỏi',          'Special', 'ST03'),
('Ba chỉ bò Mỹ sốt tỏi',             'Special', 'ST03'),
('Ba chỉ heo sốt tỏi',               'Special', 'ST03'),
('Thăn heo sốt tỏi',                 'Special', 'ST03'),
('Nầm heo sốt tỏi',                  'Special', 'ST03'),
('Nọng heo sốt tỏi',                 'Special', 'ST03'),
-- Nướng giấy bạc
('Lòng bò béo nướng giấy bạc',       'Special', 'ST03'),
('Sò điệp nướng giấy bạc',           'Special', 'ST03'),
-- Món thêm
('Bánh nếp phô mai',                 'Special', 'ST05'),
('Lạp xưởng nướng',                  'Special', 'ST03'),
('Mì udon sốt kem',                  'Special', 'ST05'),
('Tôm chiên mayo',                   'Special', 'ST05'),
('Mực chiên xù',                     'Special', 'ST05'),
('Mì cá hồi sốt kem',                'Special', 'ST05'),
('Mì udon thịt xông khói sốt kem',   'Special', 'ST05'),
('Bánh xèo trứng cá tuyết',          'Special', 'ST05'),
-- Lẩu lòng bò (3 cỡ)
('Lẩu lòng bò (Lớn)',                'Special', 'ST05'),
('Lẩu lòng bò (Trung)',              'Special', 'ST05'),
('Lẩu lòng bò (Nhỏ)',                'Special', 'ST05'),
-- Topping lẩu lòng bò (món đã có thì chỉ gắn thêm vào gói)
('Nấm kim châm',                     'Topping', 'ST05'),
('Đậu bắp',                          'Topping', 'ST05'),
('Bắp ngô',                          'Topping', 'ST05'),
('Đậu khuôn',                        'Topping', 'ST05'),
('Cải thảo',                         'Topping', 'ST05'),
('Nấm đùi gà',                       'Topping', 'ST05'),
('Lòng mỡ bò',                       'Topping', 'ST05'),
('Ba chỉ heo mỏng',                  'Thịt nướng', 'ST03');

-- Thêm vào cả 3 gói 349K, 389K, 469K
SELECT add_to_package(v.price, sp.name, sp.cat, sp.station)
FROM sp CROSS JOIN (VALUES (349000), (389000), (469000)) AS v(price);

DROP TABLE sp;


-- ---------- Kiểm tra ----------

-- Số món mỗi gói: 349K, 389K, 469K đều phải tăng thêm cùng một số món so với trước
SELECT p.price, COUNT(*) AS so_mon
FROM packages p JOIN package_items pi ON pi.package_id = p.id
GROUP BY p.price ORDER BY p.price;

-- 20 món nhóm Special (phải có mặt ở 349K, 389K, 469K; KHÔNG có ở 199K, 269K, 299K)
SELECT p.price, COUNT(*) AS so_mon_special
FROM packages p
JOIN package_items pi ON pi.package_id = p.id
JOIN menu_items m ON m.id = pi.menu_item_id
WHERE m.category = 'Special'
GROUP BY p.price ORDER BY p.price;
