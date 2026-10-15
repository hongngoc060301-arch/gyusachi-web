-- =====================================================
-- 01. TẠO BẢNG (có xoá sạch bảng cũ nếu đã tồn tại)
-- Chạy file này đầu tiên. Chạy lại bao nhiêu lần cũng được
-- (mỗi lần chạy sẽ xoá toàn bộ dữ liệu cũ).
-- =====================================================

DROP TABLE IF EXISTS order_items, orders, package_items, packages,
                     menu_items, dining_tables, staffs, stations CASCADE;
DROP FUNCTION IF EXISTS add_to_package(INT, TEXT, TEXT, TEXT);

-- Bảng a la carte / combo (file 10, 11) cũng xoá luôn để chạy lại từ đầu cho sạch
DROP TABLE IF EXISTS combo_details, alacarte_items CASCADE;
DROP FUNCTION IF EXISTS add_combo_item(VARCHAR, VARCHAR, VARCHAR, INT);


CREATE TABLE stations (
    id          VARCHAR(10) PRIMARY KEY,
    name        VARCHAR(100) NOT NULL,
    icon        VARCHAR(50),
    description VARCHAR(200),
    pin         VARCHAR(10) NOT NULL UNIQUE
);

CREATE TABLE staffs (
    id      VARCHAR(10) PRIMARY KEY,
    name    VARCHAR(100) NOT NULL,
    role    VARCHAR(50)  NOT NULL,
    pin     VARCHAR(10)  NOT NULL UNIQUE,
    avatar  VARCHAR(200)
);

CREATE TABLE dining_tables (
    id           VARCHAR(10) PRIMARY KEY,
    name         VARCHAR(50),
    capacity     INT NOT NULL,
    min_capacity INT NOT NULL DEFAULT 1,
    floor        INT NOT NULL,
    type         VARCHAR(20) NOT NULL DEFAULT 'NORMAL',
    status       VARCHAR(20) NOT NULL DEFAULT 'AVAILABLE'
);

CREATE TABLE menu_items (
    id         SERIAL PRIMARY KEY,
    name       VARCHAR(150) NOT NULL UNIQUE,
    category   VARCHAR(100) NOT NULL,
    station_id VARCHAR(10) REFERENCES stations(id),
    is_active  BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE TABLE packages (
    id    SERIAL PRIMARY KEY,
    name  VARCHAR(100) NOT NULL,
    price INT NOT NULL UNIQUE
);

CREATE TABLE package_items (
    package_id   INT NOT NULL REFERENCES packages(id) ON DELETE CASCADE,
    menu_item_id INT NOT NULL REFERENCES menu_items(id) ON DELETE CASCADE,
    PRIMARY KEY (package_id, menu_item_id)
);

CREATE TABLE orders (
    id               SERIAL PRIMARY KEY,
    table_id         VARCHAR(10) REFERENCES dining_tables(id),
    staff_id         VARCHAR(10) REFERENCES staffs(id),
    package_id       INT REFERENCES packages(id),        -- gói buffet đồ ăn (199K...469K), có thể trống nếu chỉ gọi lẻ
    drink_package_id INT REFERENCES packages(id),        -- gói buffet nước (49K / 69K / 139K), có thể trống
    guests           INT,
    status           VARCHAR(20) NOT NULL DEFAULT 'OPEN',  -- OPEN | CLOSED
    created_at       TIMESTAMP NOT NULL DEFAULT NOW(),
    closed_at        TIMESTAMP
);

-- Mỗi dòng = 1 món khách gọi. Lưu sẵn tên / trạm / giá tại thời điểm gọi
-- (để sau này đổi menu thì hoá đơn cũ không bị sai).
--   kind: PACKAGE (món trong buffet) | ALACARTE (gọi lẻ, kể cả nước)
--         COMBO (dòng tổng của combo, tính tiền) | COMBO_PART (món con, gửi bếp)
--   status: NEW (chờ bếp) | DOING (đang làm) | DONE (đã xong) | CANCELLED (đã huỷ)
CREATE TABLE order_items (
    id           SERIAL PRIMARY KEY,
    order_id     INT NOT NULL REFERENCES orders(id) ON DELETE CASCADE,
    parent_id    INT REFERENCES order_items(id) ON DELETE CASCADE,
    kind         VARCHAR(12) NOT NULL DEFAULT 'PACKAGE',
    menu_item_id INT REFERENCES menu_items(id),
    name         VARCHAR(200) NOT NULL,
    station_id   VARCHAR(10) REFERENCES stations(id),
    qty          INT NOT NULL DEFAULT 1,
    unit_price   INT NOT NULL DEFAULT 0,
    status       VARCHAR(20) NOT NULL DEFAULT 'NEW',
    note         VARCHAR(200),
    created_at   TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at   TIMESTAMP
);

CREATE INDEX idx_order_items_station ON order_items (station_id, status);
CREATE INDEX idx_order_items_order   ON order_items (order_id);

-- Mỗi bàn chỉ có tối đa 1 đơn đang mở
CREATE UNIQUE INDEX ux_orders_one_open_per_table ON orders (table_id) WHERE status = 'OPEN';


-- Kiểm tra: phải thấy 8 bảng
SELECT table_name
FROM information_schema.tables
WHERE table_schema = 'public'
ORDER BY table_name;
