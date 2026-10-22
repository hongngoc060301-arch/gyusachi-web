-- =====================================================
-- 02. DỮ LIỆU NỀN: trạm bếp, bàn, nhân viên, gói buffet
-- Chạy SAU file 01. Chỉ chạy 1 lần.
-- (Muốn chạy lại thì chạy lại file 01 trước để xoá sạch.)
-- =====================================================

INSERT INTO stations (id, name, icon, description, pin) VALUES
('ST01','Quầy Pha Chế','fa-martini-glass-citrus','Bia, nước ngọt, tráng miệng','0001'),
('ST02','Quầy Sashimi','fa-fish','Cá hồi tươi, trích ép trứng, sò đỏ','0002'),
('ST03','Quầy Thịt Nướng','fa-fire-burner','Ba chỉ bò Mỹ, dẻ sườn, sườn sụn','0003'),
('ST04','Khai vị / Salad / Sushi','fa-bowl-rice','Khai vị, Salad, Kim chi, Sushi, Nigiri','0004'),
('ST05','Bếp Nóng (Lẩu/Chiên)','fa-kitchen-set','Nồi lẩu, khoai chiên, gà sốt cay','0005');


INSERT INTO dining_tables (id, name, capacity, min_capacity, floor, type) VALUES
('A1','A1',2,1,1,'NORMAL'),
('A2','A2',4,1,1,'NORMAL'),
('A3','A3',4,1,1,'NORMAL'),
('A4','A4',4,1,1,'NORMAL'),
('A5','A5',6,1,1,'NORMAL'),
('A6','A6',6,1,1,'NORMAL'),
('A7','A7',8,1,1,'NORMAL'),
('B1','B1',6,1,2,'NORMAL'),
('B2','B2',6,1,2,'NORMAL'),
('B3','B3',6,1,2,'NORMAL'),
('B4','B4',6,1,2,'NORMAL'),
('B5','B5',6,1,2,'NORMAL'),
('B6','B6',4,1,2,'NORMAL'),
('B7','B7',4,1,2,'NORMAL'),
('B8','B8',2,1,2,'NORMAL'),
('B9','B9',2,1,2,'NORMAL'),
('B10','B10',4,1,2,'NORMAL'),
('B11','B11',4,1,2,'NORMAL'),
('V1','VIP 1',10,8,2,'VIP'),
('V2','VIP 2',10,8,2,'VIP');


INSERT INTO staffs (id, name, role, pin, avatar) VALUES
('01','Anh Khoa','Quản lí','1111','/static/images/Khoa.png'),
('02','Thuỳ Phương','Phó quản lí','2222','/static/images/Phuong.png'),
('03','Trâm Anh','Giám Sát','3333','/static/images/TAnh.png'),
('04','Hồng Ngọc','Phục vụ','4444','/static/images/Ngoc.png'),
('05','Mai Linh','Phục vụ','5555','/static/images/Linh.png'),
('06','Nguyên An','Phục vụ','6666','/static/images/An.png'),
('07','Khánh Lan','Phục vụ','7777','/static/images/Lan.png'),
('08','Anh Khiêm','Phục vụ','8888','/static/images/Khiem.png'),
('09','Khánh Hoàng','Phục vụ','9999','/static/images/Hoang.png'),
('10','Hoàng Chi','Phục vụ','1010','/static/images/Chi.png'),
('11','Hạnh Nhi','Phục vụ','1100','/static/images/Nhi.png'),
('12','Xuân Tiếp','Phục vụ','1212','/static/images/Tiep.png'),
('13','Khuyên Niê','Phục vụ','1313','/static/images/Nie.png');


INSERT INTO packages (name, price) VALUES
('Buffet 219K', 219000),
('Buffet 269K', 269000),
('Buffet 299K', 299000),
('Buffet 349K', 349000),
('Buffet 389K', 389000),
('Buffet 469K', 469000);


-- Kiểm tra: so_tram=5, so_ban=20, so_nhan_vien=13, so_goi=6
SELECT
  (SELECT COUNT(*) FROM stations)      AS so_tram,
  (SELECT COUNT(*) FROM dining_tables) AS so_ban,
  (SELECT COUNT(*) FROM staffs)        AS so_nhan_vien,
  (SELECT COUNT(*) FROM packages)      AS so_goi;
