-- =====================================================
-- 19. KHO PHỤC VỤ (file của bạn, giữ nguyên nội dung). Chạy SAU file 18.
-- Chạy lại được nhiều lần, nhưng mỗi lần chạy lại thì XOÁ và tạo mới kho phục vụ (mất số liệu kho phục vụ cũ).
-- =====================================================
BEGIN;

-- Dọn bản cũ (nếu đã chạy file này trước đó) để chạy lại không bị lỗi
DROP FUNCTION IF EXISTS chot_ngay(DATE), nhap_kho(VARCHAR, NUMERIC, TEXT), kiem_ke(VARCHAR, NUMERIC, TEXT), doi_ma_update(VARCHAR, INT, NUMERIC, VARCHAR);
DROP TABLE IF EXISTS lich_su_kho, so_khach_ngay, kho_phuc_vu, nhom_hang CASCADE;

-- =====================================================
-- 1. BẢNG
-- =====================================================

CREATE TABLE nhom_hang (
    ma_nhom   VARCHAR(10) PRIMARY KEY,
    ten_nhom  VARCHAR(100) NOT NULL,
    mo_ta     TEXT
);

CREATE TABLE kho_phuc_vu (
    ma_vt          VARCHAR(20)   PRIMARY KEY,
    ma_nhom        VARCHAR(10)   NOT NULL REFERENCES nhom_hang(ma_nhom),
    ten_vt         VARCHAR(150)  NOT NULL UNIQUE,
    dvt            VARCHAR(20)   NOT NULL,
    so_luong       NUMERIC(12,2) NOT NULL DEFAULT 0,
    ton_toi_thieu  NUMERIC(12,2) NOT NULL DEFAULT 0,
    ma_update      SMALLINT      NOT NULL DEFAULT 2 CHECK (ma_update IN (1, 2)),
    -- Dùng khi ma_update = 1 (tự trừ):
    kieu_tru       VARCHAR(5)    CHECK (kieu_tru IN ('KHACH', 'NGAY')),
    dinh_muc       NUMERIC(12,4) NOT NULL DEFAULT 0,
    ghi_chu        TEXT,
    dang_dung      BOOLEAN       NOT NULL DEFAULT TRUE,
    updated_at     TIMESTAMP     NOT NULL DEFAULT NOW(),
    -- Tự trừ thì bắt buộc có kiểu trừ và định mức > 0
    CONSTRAINT chk_tu_tru CHECK (
        ma_update = 2 OR (kieu_tru IS NOT NULL AND dinh_muc > 0)
    )
);

CREATE INDEX idx_kpv_nhom ON kho_phuc_vu(ma_nhom);

COMMENT ON COLUMN kho_phuc_vu.ma_update IS '1 = tự trừ, 2 = update thủ công';
COMMENT ON COLUMN kho_phuc_vu.kieu_tru  IS 'KHACH: trừ dinh_muc x số khách | NGAY: trừ dinh_muc mỗi ngày';

-- Số khách mỗi ngày (nguồn để trừ kiểu KHACH)
CREATE TABLE so_khach_ngay (
    ngay      DATE PRIMARY KEY,
    so_khach  INT NOT NULL CHECK (so_khach >= 0),
    ghi_chu   TEXT
);

-- Lịch sử biến động kho (số có dấu: dương = nhập, âm = xuất)
CREATE TABLE lich_su_kho (
    id          BIGSERIAL PRIMARY KEY,
    ma_vt       VARCHAR(20) NOT NULL REFERENCES kho_phuc_vu(ma_vt),
    ngay        DATE NOT NULL DEFAULT CURRENT_DATE,
    loai        VARCHAR(20) NOT NULL
                CHECK (loai IN ('NHAP', 'XUAT_TU_DONG', 'KIEM_KE')),
    so_luong    NUMERIC(12,4) NOT NULL,
    ghi_chu     TEXT,
    created_at  TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_lskho_vt_ngay ON lich_su_kho(ma_vt, ngay);

-- Mỗi vật tư chỉ trừ tự động 1 lần/ngày (chạy lại không bị trừ đôi)
CREATE UNIQUE INDEX uq_tru_tu_dong_moi_ngay
    ON lich_su_kho(ma_vt, ngay) WHERE loai = 'XUAT_TU_DONG';

-- =====================================================
-- 2. DỮ LIỆU: NHÓM HÀNG
-- =====================================================
INSERT INTO nhom_hang (ma_nhom, ten_nhom, mo_ta) VALUES
('BN', 'Bàn nướng',          'Thiết bị và phụ kiện bàn nướng tại bàn'),
('CD', 'Chén đĩa set up',    'Đĩa, tô, chén, thố dùng để bày món'),
('DC', 'Dụng cụ ăn',         'Đũa, muỗng, nĩa, ly, khăn...'),
('OR', 'Order & vận hành',   'Thiết bị order, in bill, menu, khay bưng'),
('TH', 'Vật tư tiêu hao',    'Hộp mang về, bao rác, găng tay...'),
('VS', 'Vệ sinh',            'Hóa chất và dụng cụ vệ sinh'),
('DP', 'Thiết bị dự phòng',  'Đồ dự phòng, sửa chữa nhỏ');

-- =====================================================
-- 3. VẬT TƯ + SỐ LƯỢNG  <<< SỬA SỐ Ở ĐÂY >>>
--
-- Cột:  ma_vt | ma_nhom | ten_vt | dvt | so_luong | ton_toi_thieu | ma_update | kieu_tru | dinh_muc | ghi_chu
--   so_luong       : số đang có trong kho (hiện để 0, bạn điền số thật)
--   ton_toi_thieu  : mức cảnh báo sắp hết (hiện để 0, bạn điền)
--   ma_update      : 1 = tự trừ, 2 = thủ công
--   kieu_tru       : 'KHACH' (trừ theo số khách) hoặc 'NGAY' (trừ mỗi ngày); thủ công thì NULL
--   dinh_muc       : số lượng trừ trên mỗi khách / mỗi ngày (số tạm, bạn sửa lại); thủ công thì 0
--
-- Đổi 1 món sang tự trừ:  ..., 1, 'KHACH', 0.5, ...   hoặc   ..., 1, 'NGAY', 0.5, ...
-- Đổi 1 món sang thủ công: ..., 2, NULL, 0, ...
-- =====================================================
INSERT INTO kho_phuc_vu
    (ma_vt, ma_nhom, ten_vt, dvt, so_luong, ton_toi_thieu, ma_update, kieu_tru, dinh_muc, ghi_chu)
VALUES
-- ---------- BÀN NƯỚNG ----------
('BN-001','BN','Vỉ nướng',                     'cái',   40,30,2, NULL,    0,    NULL),
('BN-002','BN','Lò Than',                      'cái',   25,22,2, NULL,    0,    NULL),
('BN-003','BN','Bếp ga bàn',                   'cái',   2, 0, 2, NULL,    0,    NULL),
('BN-004','BN','Bình ga mini',                 'bình',  10,5, 2, NULL,    0,    'Dùng cho bếp ga bàn'),
('BN-005','BN','Than nướng',                   'kg',    20,5, 1, 'KHACH', 0.15, 'Nếu dùng bếp than'),

-- ---------- CHÉN ĐĨA THEO MÓN ----------
('CD-001','CD','Đĩa lớn setup t2',             'cái',   20,14,2, NULL,    0,    NULL),
('CD-002','CD','Đĩa lớn setup t1',             'cái',   20,14,2, NULL,    0,    NULL),
('CD-003','CD','Đĩa kimchi',                   'cái',   35,30,2, NULL,    0,    NULL),
('CD-004','CD','Đĩa rau',                      'cái',   35,30,2, NULL,    0,    NULL),
('CD-005','CD','Đĩa nhỏ setup tầng 2',         'cái',   45,35,2, NULL,    0,    NULL),
('CD-006','CD','Đĩa sứ setup tầng 1',          'cái',   20,10,2, NULL,    0,    NULL),
('CD-007','CD','Chén',                         'cái',   50,40,2, NULL,    0,    NULL),
('CD-008','CD','Chén soup',                    'cái',   30,20,2, NULL,    0,    NULL),
('CD-009','CD','Chén trứng',                   'cái',   15,10,2, NULL,    0,    NULL),
('CD-010','CD','Khay 2 ngăn đen',              'cái',   30,22,2, NULL,    0,    NULL),
('CD-011','CD','Khay 2 ngăn',                  'cái',   30,22,2, NULL,    0,    NULL),
('CD-012','CD','Khay 3 ngăn',                  'cái',   45,35,2, NULL,    0,    NULL),
('CD-013','CD','Khay 1 ngăn',                  'cái',   20,10,2, NULL,    0,    NULL),
('CD-014','CD','Khay đũa muỗng',               'cái',   21,20,2, NULL,    0,    NULL),

-- ---------- DỤNG CỤ ĂN ----------
('DC-001','DC','Đũa',                          'đôi',   0, 0, 2, NULL,    0,    NULL),
('DC-002','DC','Muỗng',                        'cái',   0, 0, 2, NULL,    0,    NULL),
('DC-003','DC','Nĩa',                          'cái',   0, 0, 2, NULL,    0,    NULL),
('DC-004','DC','Muỗng kem',                    'đôi',   0, 0, 2, NULL,    0,    NULL),
('DC-005','DC','Muỗng canh',                   'cái',   0, 0, 2, NULL,    0,    NULL),
('DC-006','DC','Khăn ướt',                     'gói',   0, 0, 2, NULL,    0,    NULL),
('DC-007','DC','Khăn giấy ăn',                 'bịch',  0, 0, 2, NULL,    0,    NULL),
('DC-008','DC','Tăm',                          'gói',   0, 0, 2, NULL,    0,    NULL),
('DC-009','DC','Kẹp gắp',                      'cái',   0, 0, 2, NULL,    0,    NULL),
('DC-010','DC','Kéo',                          'cái',   0, 0, 2, NULL,    0,    NULL),

-- ---------- ORDER & VẬN HÀNH ----------
('OR-001','OR','Máy in bill',                  'cái',   6, 0, 2, NULL,    0,    NULL),
('OR-002','OR','Cuộn giấy in bill',            'cuộn',  30, 0, 1, 'KHACH', 0.02,NULL),
('OR-003','OR','Menu',                         'quyển', 170,168,2, NULL,    0,  NULL),
('OR-004','OR','Bảng số bàn',                  'cái',   21,0, 2, NULL,    0,    NULL),
('OR-005','OR','Khay bưng',                    'cái',   17,15,2, NULL,    0,    NULL),
('OR-006','OR','Thùng dọn bàn',                'cái',   12,9, 2, NULL,    0,    NULL),
('OR-007','OR','Xô dọn bàn',                   'cái',   6, 5, 2, NULL,    0,    NULL),
('OR-008','OR','Xe đẩy dọn bàn',               'cái',   2, 0, 2, NULL,    0,    NULL),
('OR-009','OR','Bong bóng',                    'bịch',  5, 0, 2, NULL,    0,    NULL),
('OR-010','OR','Dây sinh nhật',                'cái',   20,18,2, NULL,    0,    NULL),

-- ---------- VẬT TƯ TIÊU HAO ----------
('TH-001','TH','Hộp mang về',                  'cái',   50,10,2, NULL,    0,    NULL),
('TH-002','TH','Túi mang về',                  'cái',   100,0,2, NULL,    0,    NULL),
('TH-003','TH','Bao rác',                      'cái',   50,10,1, 'NGAY',  8.00, NULL),
('TH-004','TH','Găng tay',                     'hộp',   50,20,1, 'NGAY',  0.20, NULL),
('TH-005','TH','Khẩu trang',                   'hộp',   50,0, 1, 'NGAY',  0.20, NULL),
('TH-006','TH','Màn bọc thực phẩm',            'cuộn',  8, 0, 2, NULL,    0,    NULL),

-- ---------- VỆ SINH ----------
('VS-001','VS','Nước rửa chén',                'can',   8, 3, 2, NULL,    0,    NULL),
('VS-002','VS','Nước lau sàn',                 'can',   8, 3, 2, NULL,    0,    NULL),
('VS-003','VS','Nước sát khuẩn',               'chai',  8, 3, 2, NULL,    0,    NULL),
('VS-004','VS','Nước lau bàn',                 'chai',  8, 3, 2, NULL,    0,    NULL),
('VS-005','VS','Chổi',                         'cái',   3, 0, 2, NULL,    0,    NULL),
('VS-006','VS','Cây lau nhà',                  'cái',   2, 0, 2, NULL,    0,    NULL),
('VS-007','VS','Giẻ lau',                      'cái',   8, 0, 2, NULL,    0,    NULL),
('VS-008','VS','Khăn lau bàn',                 'cái',   16,10,2, NULL,    0,    NULL),
('VS-009','VS','Giấy rút',                     'cái',   20,5, 2, NULL,    0,    NULL),
('VS-010','VS','Giấy cuộn',                    'cái',   20,5, 2, NULL,    0,    NULL),
('VS-011','VS','Nước rửa tay',                 'can',   8, 3, 2, NULL,    0,    NULL),
('VS-012','VS','Sáp thơm toilet',              'cái',   10,3, 2, NULL,    0,    NULL),
('VS-013','VS','Tinh dầu',                     'cái',   5, 2, 2, NULL,    0,    NULL),

-- ---------- THIẾT BỊ DỰ PHÒNG ----------
('DP-001','DP','Bóng đèn',                     'cái',   10,3, 2, NULL,    0,    NULL),
('DP-002','DP','Pin',                          'cặp',   8, 3, 2, NULL,    0,    NULL),
('DP-003','DP','Đầu dây điện',                 'cái',   10,3, 2, NULL,    0,    NULL),
('DP-004','DP','Dụng cụ sửa chữa nhỏ',         'bộ',    5, 0, 2, NULL,    0,    NULL),
('DP-005','DP','Ghế dự phòng',                 'cái',   8, 2, 2, NULL,    0,    NULL),
('DP-006','DP','Ghế em bé',                    'cái',   5, 2, 2, NULL,    0,    NULL),
('DP-007','DP','Áo đồng phục',                 'cái',   15,5, 2, NULL,    0,    NULL),
('DP-008','DP','Tạp dề',                       'cái',   15,5, 2, NULL,    0,    NULL);
-- =====================================================
-- 4. VIEW: BẢNG KHO THEO ĐÚNG THỨ TỰ CỘT
-- =====================================================
CREATE VIEW bang_kho AS
SELECT ma_vt, ma_nhom, ten_vt, dvt, so_luong, ton_toi_thieu, ma_update
FROM kho_phuc_vu
WHERE dang_dung
ORDER BY ma_nhom, ma_vt;

-- Cảnh báo sắp hết
CREATE VIEW canh_bao_ton AS
SELECT ma_vt, ma_nhom, ten_vt, dvt, so_luong, ton_toi_thieu, ma_update
FROM kho_phuc_vu
WHERE dang_dung AND so_luong <= ton_toi_thieu
ORDER BY ma_nhom, ma_vt;

-- =====================================================
-- 5. HÀM
-- =====================================================

-- 5.1 Chốt ngày: tự trừ kho các vật tư ma_update = 1
CREATE FUNCTION chot_ngay(p_ngay DATE DEFAULT CURRENT_DATE)
RETURNS INT
LANGUAGE plpgsql
AS $$
DECLARE
    v_khach   INT;
    v_so_dong INT;
BEGIN
    SELECT so_khach INTO v_khach FROM so_khach_ngay WHERE ngay = p_ngay;
    IF v_khach IS NULL THEN
        RAISE EXCEPTION 'Chưa nhập số khách cho ngày % (bảng so_khach_ngay)', p_ngay;
    END IF;

    WITH ds AS (
        SELECT k.ma_vt,
               CASE k.kieu_tru
                    WHEN 'KHACH' THEN k.dinh_muc * v_khach
                    ELSE k.dinh_muc
               END AS sl
        FROM kho_phuc_vu k
        WHERE k.dang_dung
          AND k.ma_update = 1
          AND k.dinh_muc > 0
          AND NOT EXISTS (
              SELECT 1 FROM lich_su_kho l
              WHERE l.ma_vt = k.ma_vt AND l.ngay = p_ngay AND l.loai = 'XUAT_TU_DONG'
          )
    ),
    ghi AS (
        INSERT INTO lich_su_kho (ma_vt, ngay, loai, so_luong, ghi_chu)
        SELECT ma_vt, p_ngay, 'XUAT_TU_DONG', -sl,
               'Tự trừ ngày ' || p_ngay || ' (' || v_khach || ' khách)'
        FROM ds
        RETURNING ma_vt, so_luong          -- so_luong là số âm
    )
    UPDATE kho_phuc_vu k
    SET so_luong = k.so_luong + ghi.so_luong,
        updated_at = NOW()
    FROM ghi
    WHERE k.ma_vt = ghi.ma_vt;

    GET DIAGNOSTICS v_so_dong = ROW_COUNT;
    RETURN v_so_dong;
END;
$$;

-- 5.2 Nhập hàng về: cộng thêm vào tồn
CREATE FUNCTION nhap_kho(p_ma_vt VARCHAR, p_so_luong NUMERIC, p_ghi_chu TEXT DEFAULT NULL)
RETURNS VOID
LANGUAGE plpgsql
AS $$
BEGIN
    UPDATE kho_phuc_vu
    SET so_luong = so_luong + p_so_luong, updated_at = NOW()
    WHERE ma_vt = p_ma_vt;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Không tìm thấy vật tư %', p_ma_vt;
    END IF;

    INSERT INTO lich_su_kho (ma_vt, loai, so_luong, ghi_chu)
    VALUES (p_ma_vt, 'NHAP', p_so_luong, p_ghi_chu);
END;
$$;

-- 5.3 Kiểm kê: đặt lại tồn theo số đếm thực tế (dùng cho cả mã 1 và mã 2)
CREATE FUNCTION kiem_ke(p_ma_vt VARCHAR, p_so_thuc_te NUMERIC, p_ghi_chu TEXT DEFAULT NULL)
RETURNS VOID
LANGUAGE plpgsql
AS $$
DECLARE
    v_cu NUMERIC;
BEGIN
    SELECT so_luong INTO v_cu FROM kho_phuc_vu WHERE ma_vt = p_ma_vt;
    IF NOT FOUND THEN
        RAISE EXCEPTION 'Không tìm thấy vật tư %', p_ma_vt;
    END IF;

    UPDATE kho_phuc_vu
    SET so_luong = p_so_thuc_te, updated_at = NOW()
    WHERE ma_vt = p_ma_vt;

    INSERT INTO lich_su_kho (ma_vt, loai, so_luong, ghi_chu)
    VALUES (p_ma_vt, 'KIEM_KE', p_so_thuc_te - v_cu,
            COALESCE(p_ghi_chu, 'Kiểm kê: ' || v_cu || ' -> ' || p_so_thuc_te));
END;
$$;

-- 5.4 Đổi mã update của 1 vật tư
--   p_ma_update = 1: tự trừ (cần p_dinh_muc > 0; p_theo = 'KHACH' hoặc 'NGAY')
--   p_ma_update = 2: thủ công
CREATE FUNCTION doi_ma_update(
    p_ma_vt     VARCHAR,
    p_ma_update INT,
    p_dinh_muc  NUMERIC DEFAULT 0,
    p_theo      VARCHAR DEFAULT 'KHACH'
) RETURNS VOID
LANGUAGE plpgsql
AS $$
BEGIN
    IF p_ma_update = 2 THEN
        UPDATE kho_phuc_vu
        SET ma_update = 2, kieu_tru = NULL, dinh_muc = 0, updated_at = NOW()
        WHERE ma_vt = p_ma_vt;
    ELSIF p_ma_update = 1 THEN
        IF p_dinh_muc IS NULL OR p_dinh_muc <= 0 THEN
            RAISE EXCEPTION 'Mã update 1 (tự trừ) cần định mức > 0';
        END IF;
        UPDATE kho_phuc_vu
        SET ma_update = 1,
            kieu_tru = CASE WHEN upper(p_theo) = 'NGAY' THEN 'NGAY' ELSE 'KHACH' END,
            dinh_muc = p_dinh_muc,
            updated_at = NOW()
        WHERE ma_vt = p_ma_vt;
    ELSE
        RAISE EXCEPTION 'ma_update chỉ nhận 1 (tự trừ) hoặc 2 (thủ công)';
    END IF;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Không tìm thấy vật tư %', p_ma_vt;
    END IF;
END;
$$;

COMMIT;

-- =====================================================
-- CÁCH DÙNG
-- =====================================================
-- Xem bảng kho:
--   SELECT * FROM bang_kho;
--   SELECT * FROM bang_kho WHERE ma_update = 1;   -- món tự trừ
--   SELECT * FROM bang_kho WHERE ma_update = 2;   -- món nhập tay
--   SELECT * FROM bang_kho WHERE ma_nhom = 'DC';  -- theo nhóm
--
-- Hàng mới về, cộng thêm:
--   SELECT nhap_kho('DC-001', 200, 'Nhập đũa đợt 1');
--
-- Kiểm kê (đếm thực tế rồi ghi đè):
--   SELECT kiem_ke('CD-001', 148);
--
-- Cuối ngày: nhập số khách rồi chốt (chạy lại cùng ngày không bị trừ đôi):
--   INSERT INTO so_khach_ngay (ngay, so_khach) VALUES (CURRENT_DATE, 180)
--   ON CONFLICT (ngay) DO UPDATE SET so_khach = EXCLUDED.so_khach;
--   SELECT chot_ngay(CURRENT_DATE);               -- trả về số dòng đã trừ
--   SELECT chot_ngay('2026-10-15');               -- chốt bù ngày cũ
--
-- Đặt tồn tối thiểu:
--   UPDATE kho_phuc_vu SET ton_toi_thieu = 50 WHERE ma_vt = 'DC-001';
--
-- Đổi mã update:
--   SELECT doi_ma_update('TH-002', 1, 0.5, 'KHACH');  -- túi mang về: tự trừ 0.5/khách
--   SELECT doi_ma_update('VS-005', 1, 0.05, 'NGAY');  -- chổi: tự trừ 0.05/ngày
--   SELECT doi_ma_update('DC-008', 2);                -- tăm: chuyển về nhập tay
--
-- Thêm vật tư mới (nhập tay):
--   INSERT INTO kho_phuc_vu (ma_vt, ma_nhom, ten_vt, dvt, so_luong, ton_toi_thieu)
--   VALUES ('CD-015', 'CD', 'Tên vật tư mới', 'cái', 0, 0);
--
-- Cảnh báo sắp hết:
--   SELECT * FROM canh_bao_ton;
--
-- Xem lịch sử 1 vật tư:
--   SELECT * FROM lich_su_kho WHERE ma_vt = 'DC-006' ORDER BY id DESC;