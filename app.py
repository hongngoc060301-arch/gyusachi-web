import re
from datetime import datetime, timedelta
from pathlib import Path

from flask import Flask, render_template, request, jsonify, redirect, url_for, session

from db import query, transaction

app = Flask(__name__)
app.secret_key = 'gyusachi-do-an-tot-nghiep'     # khoá để Flask nhớ đăng nhập thu ngân


# =========================================================
# 0. HÀM HỖ TRỢ
# =========================================================

def natural_key(name):
    # Sắp xếp theo số trong tên file: "2.jpg" đứng trước "10.jpg"
    return [
        int(part) if part.isdigit() else part.lower()
        for part in re.split(r'(\d+)', name)
    ]


# Thứ tự hiển thị các nhóm món (giống thứ tự trong menu giấy)
CATEGORY_ORDER = [
    'Khai vị', 'Salad', 'Kim chi', 'Thịt nướng', 'Set Thịt Nướng', 'Hải sản nướng',
    'Sushi', 'Sashimi', 'Lẩu', 'Cơm', 'Pizza', 'Mì', 'Món ăn thêm', 'Soup',
    'Topping', 'Special', 'Tráng miệng', 'Combo',
    'Soda', 'Nước trái cây', 'Cocktail', 'Trà', 'Nước ngọt', 'Rượu', 'Bia', 'Thức uống',
]

FOOD_PACKAGE_MIN_PRICE = 150000     # từ 150K trở lên là buffet đồ ăn, dưới là buffet nước


def group_by_category(rows):
    """[{category, ...}] -> [{name, items:[...]}] theo đúng thứ tự menu."""
    groups = {}
    for r in rows:
        groups.setdefault(r['category'], []).append(r)

    def sort_key(name):
        return CATEGORY_ORDER.index(name) if name in CATEGORY_ORDER else 99

    return [{"name": name, "items": groups[name]}
            for name in sorted(groups, key=sort_key)]


class OrderError(Exception):
    """Lỗi nghiệp vụ (trả về cho người dùng đọc được)."""


def fail(message, status=400):
    return jsonify({"success": False, "message": message}), status


def get_staffs():
    # KHÔNG lấy cột pin để không gửi PIN ra trình duyệt
    rows = query("SELECT id, name, role, avatar FROM staffs ORDER BY id")
    return [dict(r) for r in rows]


def get_stations():
    # description đổi tên thành "desc" để template (st.desc) dùng như cũ
    rows = query('SELECT id, name, icon, description AS "desc" FROM stations ORDER BY id')
    return [dict(r) for r in rows]


def get_tables(floor=None):
    sql = ("SELECT id, name, capacity, min_capacity, floor, type, status "
           "FROM dining_tables")
    params = None
    if floor is not None:
        sql += " WHERE floor = %s"
        params = (floor,)
    # Xếp bàn thường theo số (B1..B11), phòng VIP đứng sau cùng
    sql += (" ORDER BY floor, (type = 'VIP'), "
            "NULLIF(regexp_replace(id, '\\D', '', 'g'), '')::int, id")
    return [dict(r) for r in query(sql, params)]


# =========================================================
# 1. TRANG CHỦ
# =========================================================

@app.route('/')
def home():
    return render_template(
        'index.html',
        staffs=get_staffs(),
        stations=get_stations(),
        tables=get_tables()
    )


# =========================================================
# 2. GỢI Ý BÀN THEO SỐ KHÁCH (trang đặt bàn)
# =========================================================

@app.route('/api/suggest-tables', methods=['POST'])
def suggest_tables():

    data = request.get_json() or {}

    try:
        guests = int(data.get('guests', 1))
    except (TypeError, ValueError):
        guests = 1

    if guests < 1:
        guests = 1

    available = [t for t in get_tables() if t["status"] == "AVAILABLE"]

    for table in available:
        if table.get("type") == "VIP":
            table["suitable"] = (
                table.get("min_capacity", 8) <= guests <= table["capacity"]
            )
        else:
            table["suitable"] = table["capacity"] >= guests

    return jsonify({
        "success": True,
        "guests": guests,
        "tables": available
    })


# =========================================================
# 3. SƠ ĐỒ TẦNG 1, TẦNG 2
# =========================================================

@app.route('/tang1')
def tang1():
    return render_template('tang1.html', tables=get_tables(floor=1))


@app.route('/tang2')
def tang2():
    return render_template('tang2.html', tables=get_tables(floor=2))


# =========================================================
# 4. XÁC THỰC PIN (nhân viên + trạm bếp) — đọc từ database
# =========================================================

@app.route('/api/verify-pin', methods=['POST'])
def verify_pin():

    data = request.get_json() or {}
    code = str(data.get('id', '')).strip()
    entered_pin = str(data.get('pin', '')).strip()

    try:
        staff = query(
            "SELECT id, name FROM staffs WHERE id = %s AND pin = %s",
            (code, entered_pin), one=True
        )
        station = query(
            "SELECT id, name FROM stations WHERE id = %s AND pin = %s",
            (code, entered_pin), one=True
        )
    except Exception as e:
        print("Lỗi database:", e)
        return jsonify({
            "success": False,
            "message": "Không kết nối được cơ sở dữ liệu!"
        })

    if staff:
        return jsonify({
            "success": True,
            "message": f"Chào mừng {staff['name']} vào ca!",
            "redirect": f"/phucvu?staff={staff['id']}"
        })

    if station:
        return jsonify({
            "success": True,
            "message": f"Chào mừng đến {station['name']}!",
            "redirect": f"/bep?station={station['id']}"
        })

    return jsonify({
        "success": False,
        "message": "Mã PIN không đúng!"
    })


# =========================================================
# 5. ẢNH MENU (buffet / a la carte / nước)
# =========================================================

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}


def list_images(folder):
    if not folder.exists():
        return []
    return sorted(
        (f.name for f in folder.iterdir()
         if f.is_file() and f.suffix.lower() in IMAGE_EXTENSIONS),
        key=natural_key
    )


@app.route('/api/menu-images/<int:price>')
def menu_images(price):

    if price not in {199, 269, 299, 349, 389, 469}:
        return jsonify({"images": []}), 404

    folder = Path(app.static_folder) / "images" / "menu" / str(price)
    return jsonify({"images": list_images(folder)})


@app.route('/api/menu-images/special')
def menu_images_special():
    """Ảnh Special Menu (áp dụng menu 349K - 389K - 469K)."""
    folder = Path(app.static_folder) / "images" / "menu" / "special"
    return jsonify({"images": list_images(folder)})


@app.route('/api/menu-category/<category>')
def menu_category(category):

    if category not in {"alacarte", "drink"}:
        return jsonify({"images": []}), 404

    folder = Path(app.static_folder) / "images" / "menu" / category
    return jsonify({"images": list_images(folder)})


# =========================================================
# 6. TRANG PHỤC VỤ / BẾP
# =========================================================

@app.route('/phucvu')
def phucvu():
    staff_id = request.args.get('staff')

    staff = query(
        "SELECT id, name, role, avatar FROM staffs WHERE id = %s",
        (staff_id,), one=True
    )

    if not staff:
        return redirect(url_for('home'))

    return render_template(
        'phucvu.html',
        staff=dict(staff),
        tables=get_tables()
    )


@app.route('/bep')
def bep():
    station_id = request.args.get('station')

    station = query(
        'SELECT id, name, icon, description AS "desc" FROM stations WHERE id = %s',
        (station_id,), one=True
    )

    if not station:
        return redirect(url_for('home'))

    return render_template('bep.html', station=dict(station))


# =========================================================
# 7. GỌI MÓN — GÓI BUFFET, MENU, MỞ BÀN, GỌI MÓN
# =========================================================

@app.route('/api/tables')
def api_tables():
    """Danh sách bàn + trạng thái hiện tại (để tô màu bàn đang dùng)."""
    rows = query("""
        SELECT t.id, t.name, t.capacity, t.min_capacity, t.floor, t.type, t.status,
               o.id AS order_id, o.guests
        FROM dining_tables t
        LEFT JOIN orders o ON o.table_id = t.id AND o.status = 'OPEN'
        ORDER BY t.floor, (t.type = 'VIP'),
                 NULLIF(regexp_replace(t.id, '\\D', '', 'g'), '')::int, t.id
    """)
    return jsonify({"tables": [dict(r) for r in rows]})


@app.route('/api/packages')
def api_packages():
    """Các gói buffet. today_ok = gói có áp dụng hôm nay không (49K: T2-T5, 69K: T6-CN)."""
    today = datetime.now().isoweekday()          # 1 = thứ 2 ... 7 = chủ nhật
    food, drink = [], []

    for r in query("SELECT id, name, price, valid_days FROM packages ORDER BY price"):
        days = [int(x) for x in (r['valid_days'] or '').split(',') if x.strip()]
        item = {
            "id": r['id'], "name": r['name'], "price": r['price'],
            "today_ok": (not days) or (today in days),
        }
        (food if r['price'] >= FOOD_PACKAGE_MIN_PRICE else drink).append(item)

    return jsonify({"food": food, "drink": drink, "today": today})


@app.route('/api/menu/package/<int:package_id>')
def api_menu_package(package_id):
    """Món có trong 1 gói buffet, chia theo nhóm."""
    rows = query("""
        SELECT m.id, m.name, m.category
        FROM package_items pi
        JOIN menu_items m ON m.id = pi.menu_item_id
        WHERE pi.package_id = %s AND m.is_active
        ORDER BY m.id
    """, (package_id,))
    return jsonify({"categories": group_by_category([dict(r) for r in rows])})


@app.route('/api/menu/alacarte')
def api_menu_alacarte():
    """Món gọi lẻ (có giá), gồm cả thức uống, set thịt và combo."""
    rows = [dict(r) for r in query("""
        SELECT id, name, category, price::int AS price
        FROM alacarte_items WHERE is_active ORDER BY id
    """)]

    parts_by_combo = {}
    for p in query("""
        SELECT id, combo_id, item_name AS name, quantity AS qty, choices
        FROM combo_details ORDER BY id
    """):
        parts_by_combo.setdefault(p['combo_id'], []).append({
            "id": p['id'], "name": p['name'], "qty": p['qty'],
            "choices": p['choices'].split('|') if p['choices'] else None,
        })

    for r in rows:
        r['parts'] = parts_by_combo.get(r['id'])      # None nếu không phải combo/set
        r['is_combo'] = r['parts'] is not None

    return jsonify({"categories": group_by_category(rows)})


def order_detail(order_id):
    o = query("""
        SELECT o.id, o.table_id, o.staff_id, o.guests, o.status,
               to_char(o.created_at, 'HH24:MI') AS opened_at,
               o.package_id,       p.name AS package_name, p.price AS package_price,
               o.drink_package_id, d.name AS drink_name,   d.price AS drink_price
        FROM orders o
        LEFT JOIN packages p ON p.id = o.package_id
        LEFT JOIN packages d ON d.id = o.drink_package_id
        WHERE o.id = %s
    """, (order_id,), one=True)

    if not o:
        return None

    items = query("""
        SELECT id, parent_id, kind, name, station_id, qty, unit_price, status, note,
               to_char(created_at, 'HH24:MI') AS time
        FROM order_items WHERE order_id = %s ORDER BY id
    """, (order_id,))

    o = dict(o)
    o['items'] = [dict(i) for i in items]
    return o


@app.route('/api/orders/by-table/<table_id>')
def api_order_by_table(table_id):
    row = query("SELECT id FROM orders WHERE table_id = %s AND status = 'OPEN'",
                (table_id,), one=True)
    return jsonify({"order": order_detail(row['id']) if row else None})


@app.route('/api/orders/<int:order_id>')
def api_order(order_id):
    o = order_detail(order_id)
    if not o:
        return fail("Không tìm thấy đơn.", 404)
    return jsonify({"success": True, "order": o})


@app.route('/api/orders/open', methods=['POST'])
def api_open_order():
    """Mở bàn: tạo đơn mới cho bàn."""
    data = request.get_json() or {}
    table_id = data.get('table_id')
    staff_id = data.get('staff_id')

    try:
        guests = int(data.get('guests', 1))
    except (TypeError, ValueError):
        return fail("Số khách không hợp lệ.")
    if not 1 <= guests <= 60:
        return fail("Số khách phải từ 1 đến 60.")

    package_id = data.get('package_id') or None
    drink_id = data.get('drink_package_id') or None

    try:
        with transaction() as cur:
            cur.execute("SELECT id FROM dining_tables WHERE id = %s FOR UPDATE", (table_id,))
            if not cur.fetchone():
                raise OrderError("Không tìm thấy bàn.")

            cur.execute("SELECT id FROM orders WHERE table_id = %s AND status = 'OPEN'", (table_id,))
            if cur.fetchone():
                raise OrderError("Bàn này đang có khách, hãy tải lại trang.")

            cur.execute("SELECT id FROM staffs WHERE id = %s", (staff_id,))
            if not cur.fetchone():
                raise OrderError("Không tìm thấy nhân viên.")

            if package_id:
                cur.execute("SELECT price FROM packages WHERE id = %s", (package_id,))
                p = cur.fetchone()
                if not p or p['price'] < FOOD_PACKAGE_MIN_PRICE:
                    raise OrderError("Gói buffet đồ ăn không hợp lệ.")

            if drink_id:
                cur.execute("SELECT price FROM packages WHERE id = %s", (drink_id,))
                p = cur.fetchone()
                if not p or p['price'] >= FOOD_PACKAGE_MIN_PRICE:
                    raise OrderError("Gói buffet nước không hợp lệ.")

            cur.execute("""
                INSERT INTO orders (table_id, staff_id, package_id, drink_package_id, guests)
                VALUES (%s, %s, %s, %s, %s) RETURNING id
            """, (table_id, staff_id, package_id, drink_id, guests))
            order_id = cur.fetchone()['id']

            cur.execute("UPDATE dining_tables SET status = 'OCCUPIED' WHERE id = %s", (table_id,))

    except OrderError as e:
        return fail(str(e))

    return jsonify({"success": True, "order": order_detail(order_id)})


@app.route('/api/orders/<int:order_id>/change-package', methods=['POST'])
def api_change_package(order_id):
    """Đổi vé buffet (đồ ăn và/hoặc nước) khi bàn đang gọi món.
    Món đã gọi giữ nguyên; nếu có món (chưa huỷ) không nằm trong gói mới thì không cho đổi."""
    data = request.get_json() or {}
    package_id = data.get('package_id') or None
    drink_id = data.get('drink_package_id') or None

    try:
        with transaction() as cur:
            cur.execute("SELECT id, status, package_id, drink_package_id FROM orders WHERE id = %s FOR UPDATE",
                        (order_id,))
            order = cur.fetchone()
            if not order:
                raise OrderError("Không tìm thấy đơn.")
            if order['status'] != 'OPEN':
                raise OrderError("Đơn này đã kết thúc.")
            if package_id == order['package_id'] and drink_id == order['drink_package_id']:
                raise OrderError("Bạn chưa chọn vé khác với vé hiện tại.")

            if package_id:
                cur.execute("SELECT price FROM packages WHERE id = %s", (package_id,))
                p = cur.fetchone()
                if not p or p['price'] < FOOD_PACKAGE_MIN_PRICE:
                    raise OrderError("Gói buffet đồ ăn không hợp lệ.")

            if drink_id:
                cur.execute("SELECT price, valid_days FROM packages WHERE id = %s", (drink_id,))
                p = cur.fetchone()
                if not p or p['price'] >= FOOD_PACKAGE_MIN_PRICE:
                    raise OrderError("Gói buffet nước không hợp lệ.")
                if drink_id != order['drink_package_id']:
                    days = [int(x) for x in (p['valid_days'] or '').split(',') if x.strip()]
                    if days and datetime.now().isoweekday() not in days:
                        raise OrderError("Gói nước này không áp dụng hôm nay.")

            # món buffet đã gọi mà gói mới không có -> chặn
            new_pkgs = [x for x in (package_id, drink_id) if x]
            cur.execute("""
                SELECT DISTINCT oi.name
                FROM order_items oi
                WHERE oi.order_id = %s AND oi.kind = 'PACKAGE' AND oi.status <> 'CANCELLED'
                  AND NOT EXISTS (
                      SELECT 1 FROM package_items pi
                      WHERE pi.menu_item_id = oi.menu_item_id AND pi.package_id = ANY(%s))
                ORDER BY oi.name
            """, (order_id, new_pkgs))
            bad = [r['name'] for r in cur.fetchall()]
            if bad:
                shown = ', '.join(bad[:5]) + ('...' if len(bad) > 5 else '')
                raise OrderError(f"Bàn đã gọi {len(bad)} món không có trong vé mới ({shown}). "
                                 "Huỷ các món đó (nếu bếp chưa làm) rồi đổi lại.")

            cur.execute("UPDATE orders SET package_id = %s, drink_package_id = %s WHERE id = %s",
                        (package_id, drink_id, order_id))

    except OrderError as e:
        return fail(str(e))

    return jsonify({"success": True, "order": order_detail(order_id)})


@app.route('/api/orders/<int:order_id>/items', methods=['POST'])
def api_add_items(order_id):
    """Gửi món xuống bếp. Mỗi món: {type:'PACKAGE'|'ALACARTE', id, qty, choices:{partId: 'tên'}}"""
    data = request.get_json() or {}
    items = data.get('items') or []

    if not items:
        return fail("Chưa chọn món nào.")

    try:
        with transaction() as cur:
            cur.execute("""SELECT id, package_id, drink_package_id, status
                           FROM orders WHERE id = %s FOR UPDATE""", (order_id,))
            order = cur.fetchone()
            if not order:
                raise OrderError("Không tìm thấy đơn.")
            if order['status'] != 'OPEN':
                raise OrderError("Đơn này đã kết thúc.")

            package_ids = [p for p in (order['package_id'], order['drink_package_id']) if p]

            for it in items:
                try:
                    qty = int(it.get('qty', 1))
                except (TypeError, ValueError):
                    raise OrderError("Số lượng không hợp lệ.")
                if not 1 <= qty <= 99:
                    raise OrderError("Số lượng mỗi món phải từ 1 đến 99.")

                kind = it.get('type')
                item_id = it.get('id')
                note = (it.get('note') or '').strip()[:200] or None

                # ---- món trong buffet ----
                if kind == 'PACKAGE':
                    if not package_ids:
                        raise OrderError("Bàn này chưa chọn gói buffet.")
                    cur.execute("""
                        SELECT m.id, m.name, m.station_id
                        FROM menu_items m
                        JOIN package_items pi ON pi.menu_item_id = m.id
                        WHERE m.id = %s AND m.is_active AND pi.package_id = ANY(%s)
                    """, (item_id, package_ids))
                    m = cur.fetchone()
                    if not m:
                        raise OrderError("Món không nằm trong gói buffet của bàn.")
                    cur.execute("""
                        INSERT INTO order_items (order_id, kind, menu_item_id, name, station_id, qty, unit_price, note)
                        VALUES (%s, 'PACKAGE', %s, %s, %s, %s, 0, %s)
                    """, (order_id, m['id'], m['name'], m['station_id'], qty, note))

                # ---- món gọi lẻ / combo ----
                elif kind == 'ALACARTE':
                    cur.execute("""SELECT id, name, station_code, price::int AS price, is_active
                                   FROM alacarte_items WHERE id = %s""", (item_id,))
                    a = cur.fetchone()
                    if not a:
                        raise OrderError("Không tìm thấy món gọi lẻ.")
                    if not a['is_active']:
                        raise OrderError(f"Món \"{a['name']}\" tạm hết, hãy bỏ khỏi giỏ.")

                    cur.execute("""SELECT id, item_name, station_code, quantity, choices
                                   FROM combo_details WHERE combo_id = %s ORDER BY id""", (a['id'],))
                    parts = cur.fetchall()

                    if not parts:
                        cur.execute("""
                            INSERT INTO order_items (order_id, kind, name, station_id, qty, unit_price, note)
                            VALUES (%s, 'ALACARTE', %s, %s, %s, %s, %s)
                        """, (order_id, a['name'], a['station_code'], qty, a['price'], note))
                        continue

                    # combo: 1 dòng tổng (tính tiền) + các dòng con (gửi bếp)
                    cur.execute("""
                        INSERT INTO order_items (order_id, kind, name, station_id, qty, unit_price, note)
                        VALUES (%s, 'COMBO', %s, NULL, %s, %s, %s) RETURNING id
                    """, (order_id, a['name'], qty, a['price'], note))
                    parent_id = cur.fetchone()['id']

                    chosen = it.get('choices') or {}
                    for p in parts:
                        name = p['item_name']
                        if p['choices']:
                            options = p['choices'].split('|')
                            pick = chosen.get(str(p['id']))
                            if pick not in options:
                                raise OrderError(f"Hãy chọn món cho: {p['item_name']}")
                            name = pick
                        cur.execute("""
                            INSERT INTO order_items (order_id, parent_id, kind, name, station_id, qty, unit_price)
                            VALUES (%s, %s, 'COMBO_PART', %s, %s, %s, 0)
                        """, (order_id, parent_id, name, p['station_code'], p['quantity'] * qty))

                else:
                    raise OrderError("Loại món không hợp lệ.")

    except OrderError as e:
        return fail(str(e))

    return jsonify({"success": True, "order": order_detail(order_id)})


@app.route('/api/order-items/<int:item_id>/cancel', methods=['POST'])
def api_cancel_item(item_id):
    """Huỷ món — chỉ huỷ được khi bếp CHƯA nhận làm (trạng thái NEW)."""
    try:
        with transaction() as cur:
            cur.execute("SELECT id, order_id, kind, status FROM order_items WHERE id = %s FOR UPDATE",
                        (item_id,))
            it = cur.fetchone()
            if not it:
                raise OrderError("Không tìm thấy món.")
            if it['kind'] == 'COMBO_PART':
                raise OrderError("Hãy huỷ cả combo, không huỷ riêng từng món trong combo.")

            if it['kind'] == 'COMBO':
                cur.execute("SELECT COUNT(*) AS n FROM order_items WHERE parent_id = %s AND status <> 'NEW'",
                            (item_id,))
                if cur.fetchone()['n'] > 0:
                    raise OrderError("Bếp đã làm một phần combo, không huỷ được nữa.")
                cur.execute("""UPDATE order_items SET status = 'CANCELLED', updated_at = NOW()
                               WHERE id = %s OR parent_id = %s""", (item_id, item_id))
            else:
                if it['status'] != 'NEW':
                    raise OrderError("Bếp đã nhận làm món này, không huỷ được nữa.")
                cur.execute("UPDATE order_items SET status = 'CANCELLED', updated_at = NOW() WHERE id = %s",
                            (item_id,))
            order_id = it['order_id']
    except OrderError as e:
        return fail(str(e))

    return jsonify({"success": True, "order": order_detail(order_id)})


# =========================================================
# 8. BẾP NHẬN MÓN
# =========================================================

@app.route('/api/kitchen/<station_id>')
def api_kitchen(station_id):
    """Các món của 1 trạm: chờ làm, đang làm, và đã xong trong 30 phút gần nhất."""
    rows = query("""
        SELECT oi.id, o.table_id AS "table",
               CASE WHEN oi.parent_id IS NULL THEN oi.name
                    ELSE oi.name || ' (' || p.name || ')' END AS name,
               oi.qty, oi.status, oi.note,
               to_char(oi.created_at, 'HH24:MI') AS time
        FROM order_items oi
        JOIN orders o ON o.id = oi.order_id
        LEFT JOIN order_items p ON p.id = oi.parent_id
        WHERE oi.station_id = %s
          AND o.status = 'OPEN'
          AND oi.status IN ('NEW', 'DOING', 'DONE')
          AND (oi.status <> 'DONE' OR oi.updated_at > NOW() - INTERVAL '30 minutes')
        ORDER BY oi.created_at, oi.id
    """, (station_id,))
    return jsonify({"items": [dict(r) for r in rows]})


@app.route('/api/kitchen/item/<int:item_id>/status', methods=['POST'])
def api_kitchen_status(item_id):
    """Bếp đổi trạng thái: NEW -> DOING -> DONE (không đi lùi)."""
    data = request.get_json() or {}
    new_status = data.get('status')
    station_id = data.get('station_id')

    flow = {'DOING': 'NEW', 'DONE': 'DOING'}      # trạng thái mới -> trạng thái trước đó bắt buộc
    if new_status not in flow:
        return fail("Trạng thái không hợp lệ.")

    with transaction() as cur:
        cur.execute("""
            UPDATE order_items SET status = %s, updated_at = NOW()
            WHERE id = %s AND station_id = %s AND status = %s
            RETURNING id
        """, (new_status, item_id, station_id, flow[new_status]))
        done = cur.fetchone()

    if not done:
        return fail("Món đã đổi trạng thái hoặc bị huỷ, hãy tải lại.", 409)
    return jsonify({"success": True})



# =========================================================
# 8B. THU NGÂN — TÍNH TIỀN, THANH TOÁN
# =========================================================
# Chỉnh các hằng số này khi nhà hàng đổi chính sách.

CASHIER_PASSWORD = '1234'                                # mật khẩu quầy thu ngân
VAT_RATE = 0.08                                          # VAT 8%
LUNCH_END_HOUR = 15                                      # mở bàn trước 15:00 là buffet trưa
GROUP_SIZE = 4                                           # đi 4 ...
PAY_METHODS = ('CASH', 'CARD', 'TRANSFER')

# Ngày lễ KHÔNG áp dụng "đi 4 tính 3". 'MM-DD' = lặp mỗi năm, 'YYYY-MM-DD' = riêng năm đó.
HOLIDAYS_YEARLY = {'01-01', '04-30', '05-01', '09-02', '12-24', '12-25'}
HOLIDAYS_ONCE = {f'2027-02-{d:02d}' for d in range(5, 12)}      # Tết Đinh Mùi 2027 (30 Tết - mùng 5)


def is_holiday(d):
    return d.strftime('%m-%d') in HOLIDAYS_YEARLY or d.strftime('%Y-%m-%d') in HOLIDAYS_ONCE


def promo_auto(opened_at):
    """Ưu đãi "đi 4 tính 3" có áp dụng cho bàn mở lúc opened_at không? -> (True/False, lý do)."""
    if isinstance(opened_at, str):
        opened_at = datetime.fromisoformat(opened_at)
    if is_holiday(opened_at.date()):
        return False, "Ngày lễ - không áp dụng đi 4 tính 3"
    if opened_at.hour < LUNCH_END_HOUR:
        return True, "Buffet trưa - đi 4 tính 3"
    if opened_at.weekday() <= 3:                         # 0 = thứ 2 ... 3 = thứ 5
        return True, "Buffet tối T2-T5 - đi 4 tính 3"
    return False, "Buffet tối T6-CN không áp dụng đi 4 tính 3"


def compute_bill(o, items, guests=None, promo=None):
    """Tính hoá đơn. o: dòng đơn (có created_at dạng datetime), items: các dòng order_items.
    promo: None = tự động theo giờ/ngày, True = ép áp dụng, False = ép bỏ."""
    guests = int(guests or o['guests'] or 1)
    food_price = int(o['package_price'] or 0)
    drink_price = int(o['drink_price'] or 0)

    lines = []
    for i in items:
        if i['parent_id'] is None and i['kind'] in ('ALACARTE', 'COMBO') and i['status'] != 'CANCELLED':
            lines.append({"name": i['name'], "qty": i['qty'], "unit_price": int(i['unit_price']),
                          "amount": int(i['unit_price']) * i['qty']})

    food_amount = food_price * guests
    drink_amount = drink_price * guests
    extra_amount = sum(l['amount'] for l in lines)

    auto_ok, auto_reason = promo_auto(o['created_at'])
    apply = auto_ok if promo is None else bool(promo)
    free = guests // GROUP_SIZE if (apply and food_price) else 0
    discount = free * food_price

    subtotal = food_amount + drink_amount + extra_amount
    taxable = subtotal - discount
    vat = int(round(taxable * VAT_RATE))

    if free:
        note = f"{auto_reason if promo is None else 'Thu ngân áp dụng đi 4 tính 3'}: miễn phí {free} suất"
    elif promo is False:
        note = "Thu ngân bỏ ưu đãi đi 4 tính 3"
    else:
        note = auto_reason

    return {
        "guests": guests,
        "food_name": o['package_name'], "food_price": food_price, "food_amount": food_amount,
        "drink_name": o['drink_name'], "drink_price": drink_price, "drink_amount": drink_amount,
        "lines": lines, "extra_amount": extra_amount,
        "promo_auto": auto_ok, "promo_applied": bool(free), "promo_free": free,
        "promo_note": note, "discount": discount,
        "subtotal": subtotal, "vat_rate": VAT_RATE, "vat": vat, "total": taxable + vat,
    }


def load_order_for_bill(order_id, cur=None):
    """Đọc đơn + món để tính bill. Có cur thì đọc trong transaction (khoá dòng đơn)."""
    sql_o = """
        SELECT o.id, o.table_id, o.guests, o.status, o.created_at,
               to_char(o.created_at, 'HH24:MI DD/MM') AS opened_at,
               p.name AS package_name, p.price AS package_price,
               d.name AS drink_name,   d.price AS drink_price
        FROM orders o
        LEFT JOIN packages p ON p.id = o.package_id
        LEFT JOIN packages d ON d.id = o.drink_package_id
        WHERE o.id = %s""" + (" FOR UPDATE OF o" if cur else "")
    sql_i = """SELECT id, parent_id, kind, name, qty, unit_price, status
               FROM order_items WHERE order_id = %s ORDER BY id"""
    if cur:
        cur.execute(sql_o, (order_id,)); o = cur.fetchone()
        cur.execute(sql_i, (order_id,)); items = cur.fetchall()
    else:
        o = query(sql_o, (order_id,), one=True)
        items = query(sql_i, (order_id,))
    return o, items


def parse_promo(v):
    """'on' -> True, 'off' -> False, còn lại -> None (tự động)."""
    return True if v in ('on', True) else False if v in ('off', False) else None


def pending_count(items):
    return sum(1 for i in items if i['parent_id'] is not None or i['kind'] in ('PACKAGE', 'ALACARTE')
               if i['status'] in ('NEW', 'DOING'))


@app.route('/thungan')
def thungan():
    return render_template('thungan.html')


@app.route('/api/cashier/login', methods=['POST'])
def api_cashier_login():
    pw = str((request.get_json() or {}).get('password', '')).strip()
    if pw != CASHIER_PASSWORD:
        return fail("Mật khẩu không đúng.", 401)
    session['cashier'] = True
    return jsonify({"success": True})


@app.route('/api/cashier/me')
def api_cashier_me():
    return jsonify({"logged_in": bool(session.get('cashier'))})


@app.route('/api/cashier/logout', methods=['POST'])
def api_cashier_logout():
    session.pop('cashier', None)
    return jsonify({"success": True})


@app.route('/api/cashier/orders')
def api_cashier_orders():
    """Các bàn đang có khách + tạm tính."""
    out = []
    for r in query("SELECT id FROM orders WHERE status = 'OPEN' ORDER BY created_at"):
        o, items = load_order_for_bill(r['id'])
        b = compute_bill(o, items)
        out.append({"id": o['id'], "table_id": o['table_id'], "guests": o['guests'],
                    "opened_at": o['opened_at'], "package_name": o['package_name'],
                    "total": b['total'], "pending": pending_count(items)})
    return jsonify({"orders": out})


@app.route('/api/cashier/bill/<int:order_id>')
def api_cashier_bill(order_id):
    o, items = load_order_for_bill(order_id)
    if not o:
        return fail("Không tìm thấy đơn.", 404)
    try:
        guests = int(request.args.get('guests') or o['guests'])
    except ValueError:
        return fail("Số khách không hợp lệ.")
    if not 1 <= guests <= 60:
        return fail("Số khách phải từ 1 đến 60.")
    b = compute_bill(o, items, guests, parse_promo(request.args.get('promo')))
    b.update({"order_id": o['id'], "table_id": o['table_id'], "status": o['status'],
              "opened_at": o['opened_at'], "pending": pending_count(items)})
    return jsonify({"success": True, "bill": b})


@app.route('/api/cashier/pay/<int:order_id>', methods=['POST'])
def api_cashier_pay(order_id):
    data = request.get_json() or {}
    method = data.get('method')
    if method not in PAY_METHODS:
        return fail("Hãy chọn hình thức thanh toán.")

    try:
        with transaction() as cur:
            if not session.get('cashier'):
                raise OrderError("Hết phiên đăng nhập, hãy đăng nhập lại quầy thu ngân.")

            o, items = load_order_for_bill(order_id, cur)
            if not o:
                raise OrderError("Không tìm thấy đơn.")
            if o['status'] != 'OPEN':
                raise OrderError("Đơn này đã thanh toán rồi.")

            if pending_count(items) and not data.get('force'):
                raise OrderError("PENDING")

            try:
                guests = int(data.get('guests') or o['guests'])
            except (TypeError, ValueError):
                raise OrderError("Số khách không hợp lệ.")
            if not 1 <= guests <= 60:
                raise OrderError("Số khách phải từ 1 đến 60.")

            b = compute_bill(o, items, guests, parse_promo(data.get('promo')))

            cur.execute("""
                UPDATE orders SET status = 'CLOSED', closed_at = NOW(), paid_at = NOW(),
                       guests = %s, payment_method = %s, cashier_id = %s,
                       food_amount = %s, drink_amount = %s, extra_amount = %s,
                       discount = %s, vat_amount = %s, total = %s, promo_note = %s
                WHERE id = %s
            """, (guests, method, None, b['food_amount'], b['drink_amount'], b['extra_amount'],
                  b['discount'], b['vat'], b['total'], b['promo_note'], order_id))
            cur.execute("UPDATE dining_tables SET status = 'AVAILABLE' WHERE id = %s", (o['table_id'],))

    except OrderError as e:
        if str(e) == "PENDING":
            return jsonify({"success": False, "pending": True,
                            "message": "Bàn còn món bếp chưa làm xong. Vẫn thanh toán?"}), 409
        return fail(str(e))

    return jsonify({"success": True, "total": b['total']})


@app.route('/api/cashier/history')
def api_cashier_history():
    """Các hoá đơn đã thanh toán trong hôm nay + tổng kết."""
    rows = query("""
        SELECT o.id, o.table_id, o.guests, o.payment_method, o.total, o.discount,
               to_char(o.paid_at, 'HH24:MI') AS paid_time, COALESCE(s.name, 'Thu ngân') AS cashier
        FROM orders o LEFT JOIN staffs s ON s.id = o.cashier_id
        WHERE o.paid_at::date = CURRENT_DATE
        ORDER BY o.paid_at DESC
    """)
    rows = [dict(r) for r in rows]
    by_method = {m: sum(r['total'] for r in rows if r['payment_method'] == m) for m in PAY_METHODS}
    return jsonify({"orders": rows, "count": len(rows),
                    "revenue": sum(r['total'] for r in rows), "by_method": by_method})


# =========================================================
# 8C. QUẢN LÍ — DASHBOARD, BÁO CÁO, THỐNG KÊ MÓN, THỰC ĐƠN
# =========================================================

MANAGER_PASSWORD = '88889999'                            # mật khẩu phân hệ quản lí

PAID = "o.status = 'CLOSED' AND o.paid_at IS NOT NULL"   # điều kiện: hoá đơn đã thanh toán


def manager_ok():
    return bool(session.get('manager'))


@app.route('/quanli')
def quanli():
    return render_template('quanli.html')


@app.route('/api/manager/login', methods=['POST'])
def api_manager_login():
    pw = str((request.get_json() or {}).get('password', '')).strip()
    if pw != MANAGER_PASSWORD:
        return fail("Mật khẩu không đúng.", 401)
    session['manager'] = True
    return jsonify({"success": True})


@app.route('/api/manager/me')
def api_manager_me():
    return jsonify({"logged_in": manager_ok()})


@app.route('/api/manager/logout', methods=['POST'])
def api_manager_logout():
    session.pop('manager', None)
    return jsonify({"success": True})


@app.before_request
def guard_manager_api():
    """Mọi API /api/manager/* (trừ đăng nhập / kiểm tra / đăng xuất) cần đã nhập mật khẩu quản lí."""
    if request.path.startswith('/api/manager/') and \
            request.path not in ('/api/manager/login', '/api/manager/me', '/api/manager/logout'):
        if not manager_ok():
            return fail("Hết phiên đăng nhập, hãy đăng nhập lại.", 401)


def date_range():
    """Đọc ?from=YYYY-MM-DD&to=YYYY-MM-DD (mặc định 7 ngày gần nhất). Trả (from, to) dạng chuỗi."""
    today = datetime.now().date()
    try:
        d_to = datetime.strptime(request.args.get('to', ''), '%Y-%m-%d').date()
    except ValueError:
        d_to = today
    try:
        d_from = datetime.strptime(request.args.get('from', ''), '%Y-%m-%d').date()
    except ValueError:
        d_from = d_to - timedelta(days=6)
    if d_from > d_to:
        d_from, d_to = d_to, d_from
    if (d_to - d_from).days > 366:
        d_from = d_to - timedelta(days=366)
    return d_from.isoformat(), d_to.isoformat()


def daily_series(d_from, d_to):
    rows = query(f"""
        SELECT to_char(g.d, 'YYYY-MM-DD') AS day,
               COALESCE(SUM(o.total), 0)::bigint AS revenue, COUNT(o.id)::int AS bills
        FROM generate_series(%s::date, %s::date, '1 day') AS g(d)
        LEFT JOIN orders o ON o.paid_at::date = g.d AND {PAID}
        GROUP BY g.d ORDER BY g.d
    """, (d_from, d_to))
    return [dict(r) for r in rows]


# ---------- 1. TỔNG QUAN ----------

@app.route('/api/manager/overview')
def api_manager_overview():
    periods = {
        "today": "o.paid_at >= CURRENT_DATE",
        "week":  "o.paid_at >= date_trunc('week', CURRENT_DATE)",
        "month": "o.paid_at >= date_trunc('month', CURRENT_DATE)",
    }
    out = {}
    for key, cond in periods.items():
        r = query(f"""SELECT COALESCE(SUM(o.total), 0)::bigint AS revenue, COUNT(*)::int AS bills,
                             COALESCE(SUM(o.guests), 0)::int AS guests
                      FROM orders o WHERE {PAID} AND {cond}""", one=True)
        r = dict(r)
        r['avg'] = int(r['revenue'] / r['bills']) if r['bills'] else 0
        out[key] = r

    open_row = query("""SELECT COUNT(*)::int AS tables, COALESCE(SUM(guests), 0)::int AS guests
                        FROM orders WHERE status = 'OPEN'""", one=True)
    all_tables = query("SELECT COUNT(*)::int AS n FROM dining_tables", one=True)['n']

    today = datetime.now().date()
    series = daily_series((today - timedelta(days=13)).isoformat(), today.isoformat())

    top = query(f"""
        SELECT oi.name, SUM(oi.qty)::int AS qty
        FROM order_items oi JOIN orders o ON o.id = oi.order_id
        WHERE {PAID} AND o.paid_at >= CURRENT_DATE AND oi.status <> 'CANCELLED'
          AND oi.kind IN ('PACKAGE', 'ALACARTE', 'COMBO_PART')
        GROUP BY oi.name ORDER BY qty DESC, oi.name LIMIT 5""")

    return jsonify({**out, "open": dict(open_row), "total_tables": all_tables,
                    "series": series, "top_today": [dict(r) for r in top]})


# ---------- 2. BÁO CÁO DOANH THU ----------

@app.route('/api/manager/report')
def api_manager_report():
    d_from, d_to = date_range()
    rng = "o.paid_at::date BETWEEN %s AND %s"
    p = (d_from, d_to)

    s = dict(query(f"""
        SELECT COALESCE(SUM(o.total), 0)::bigint AS revenue, COUNT(*)::int AS bills,
               COALESCE(SUM(o.guests), 0)::int AS guests,
               COALESCE(SUM(o.food_amount), 0)::bigint AS food,
               COALESCE(SUM(o.drink_amount), 0)::bigint AS drink,
               COALESCE(SUM(o.extra_amount), 0)::bigint AS extra,
               COALESCE(SUM(o.discount), 0)::bigint AS discount,
               COALESCE(SUM(o.vat_amount), 0)::bigint AS vat
        FROM orders o WHERE {PAID} AND {rng}""", p, one=True))
    s['avg'] = int(s['revenue'] / s['bills']) if s['bills'] else 0

    by_method = [dict(r) for r in query(f"""
        SELECT o.payment_method AS name, COALESCE(SUM(o.total), 0)::bigint AS revenue, COUNT(*)::int AS bills
        FROM orders o WHERE {PAID} AND {rng} GROUP BY o.payment_method ORDER BY revenue DESC""", p)]

    by_package = [dict(r) for r in query(f"""
        SELECT COALESCE(pk.name, 'Chỉ gọi lẻ') AS name, COALESCE(SUM(o.total), 0)::bigint AS revenue,
               COUNT(*)::int AS bills, COALESCE(SUM(o.guests), 0)::int AS guests
        FROM orders o LEFT JOIN packages pk ON pk.id = o.package_id
        WHERE {PAID} AND {rng} GROUP BY pk.name, pk.price ORDER BY pk.price NULLS FIRST""", p)]

    by_shift = [dict(r) for r in query(f"""
        SELECT CASE WHEN EXTRACT(HOUR FROM o.created_at) < {LUNCH_END_HOUR} THEN 'Trưa' ELSE 'Tối' END AS name,
               COALESCE(SUM(o.total), 0)::bigint AS revenue, COUNT(*)::int AS bills
        FROM orders o WHERE {PAID} AND {rng} GROUP BY 1 ORDER BY 1 DESC""", p)]

    invoices = [dict(r) for r in query(f"""
        SELECT o.id, o.table_id, o.guests, o.payment_method, o.total, o.discount,
               to_char(o.paid_at, 'DD/MM HH24:MI') AS paid_time, COALESCE(pk.name, 'Chỉ gọi lẻ') AS package
        FROM orders o LEFT JOIN packages pk ON pk.id = o.package_id
        WHERE {PAID} AND {rng} ORDER BY o.paid_at DESC LIMIT 300""", p)]

    return jsonify({"from": d_from, "to": d_to, "summary": s, "by_method": by_method,
                    "by_package": by_package, "by_shift": by_shift,
                    "series": daily_series(d_from, d_to), "invoices": invoices})


@app.route('/api/manager/invoice/<int:order_id>')
def api_manager_invoice(order_id):
    o = query("""
        SELECT o.id, o.table_id, o.guests, o.payment_method, o.status, o.promo_note,
               to_char(o.created_at, 'DD/MM HH24:MI') AS opened_at,
               to_char(o.paid_at, 'DD/MM HH24:MI') AS paid_at,
               o.food_amount, o.drink_amount, o.extra_amount, o.discount, o.vat_amount, o.total,
               pk.name AS package_name, pk.price AS package_price,
               dk.name AS drink_name,   dk.price AS drink_price
        FROM orders o
        LEFT JOIN packages pk ON pk.id = o.package_id
        LEFT JOIN packages dk ON dk.id = o.drink_package_id
        WHERE o.id = %s""", (order_id,), one=True)
    if not o:
        return fail("Không tìm thấy hoá đơn.", 404)
    lines = query("""
        SELECT name, qty, unit_price::int AS unit_price, (qty * unit_price)::int AS amount
        FROM order_items
        WHERE order_id = %s AND parent_id IS NULL AND kind IN ('ALACARTE', 'COMBO') AND status <> 'CANCELLED'
        ORDER BY id""", (order_id,))
    return jsonify({"success": True, "invoice": dict(o), "lines": [dict(l) for l in lines]})


# ---------- 3. THỐNG KÊ MÓN ----------

@app.route('/api/manager/dishes')
def api_manager_dishes():
    d_from, d_to = date_range()
    p = (d_from, d_to)
    base = f"""FROM order_items oi JOIN orders o ON o.id = oi.order_id
               WHERE {PAID} AND o.paid_at::date BETWEEN %s AND %s"""

    buffet = query(f"""SELECT oi.name, SUM(oi.qty)::int AS qty {base}
                       AND oi.kind = 'PACKAGE' AND oi.status <> 'CANCELLED'
                       GROUP BY oi.name ORDER BY qty DESC, oi.name LIMIT 15""", p)

    paid_items = query(f"""
        SELECT oi.name, COALESCE(MAX(a.category), '') AS category, SUM(oi.qty)::int AS qty,
               SUM(oi.qty * oi.unit_price)::bigint AS revenue
        {base} AND oi.parent_id IS NULL AND oi.kind IN ('ALACARTE', 'COMBO') AND oi.status <> 'CANCELLED'
        GROUP BY oi.name ORDER BY revenue DESC, oi.name""".replace(
        "FROM order_items oi JOIN orders o ON o.id = oi.order_id",
        "FROM order_items oi JOIN orders o ON o.id = oi.order_id LEFT JOIN alacarte_items a ON a.name = oi.name"), p)
    paid_items = [dict(r) for r in paid_items]

    by_cat = {}
    for r in paid_items:
        c = r['category'] or 'Khác'
        by_cat[c] = by_cat.get(c, 0) + r['revenue']
    by_category = sorted(({"name": k, "revenue": v} for k, v in by_cat.items()),
                         key=lambda x: -x['revenue'])

    cancelled = query(f"""SELECT oi.name, SUM(oi.qty)::int AS qty {base}
                          AND oi.parent_id IS NULL AND oi.status = 'CANCELLED'
                          GROUP BY oi.name ORDER BY qty DESC, oi.name LIMIT 15""", p)
    cancelled_total = query(f"""SELECT COALESCE(SUM(oi.qty), 0)::int AS n {base}
                                AND oi.parent_id IS NULL AND oi.status = 'CANCELLED'""", p, one=True)['n']

    return jsonify({"from": d_from, "to": d_to,
                    "buffet": [dict(r) for r in buffet],
                    "paid_top": paid_items[:15], "by_category": by_category,
                    "cancelled": [dict(r) for r in cancelled], "cancelled_total": cancelled_total})


# ---------- 4. QUẢN LÍ THỰC ĐƠN ----------

@app.route('/api/manager/menu')
def api_manager_menu():
    ala = query("""
        SELECT a.id, a.name, a.category, a.price::int AS price, a.is_active,
               EXISTS (SELECT 1 FROM combo_details c WHERE c.combo_id = a.id) AS is_combo
        FROM alacarte_items a ORDER BY a.id""")
    buffet = query("""
        SELECT m.id, m.name, m.category, m.is_active, MIN(p.price)::int AS from_price
        FROM menu_items m
        LEFT JOIN package_items pi ON pi.menu_item_id = m.id
        LEFT JOIN packages p ON p.id = pi.package_id
        GROUP BY m.id ORDER BY m.id""")
    stations = query("SELECT id, name FROM stations ORDER BY id")
    packages = query("SELECT id, name, price FROM packages ORDER BY price")
    return jsonify({"alacarte": [dict(r) for r in ala], "buffet": [dict(r) for r in buffet],
                    "category_order": CATEGORY_ORDER,
                    "stations": [dict(r) for r in stations], "packages": [dict(r) for r in packages]})


def clean_name(v, limit):
    """Tên món: bỏ khoảng trắng thừa, không được rỗng."""
    v = ' '.join(str(v or '').split())
    if not v:
        raise OrderError("Hãy nhập tên.")
    if len(v) > limit:
        raise OrderError(f"Tên quá dài (tối đa {limit} ký tự).")
    return v


@app.route('/api/manager/alacarte/new', methods=['POST'])
def api_manager_alacarte_new():
    """Thêm món gọi lẻ / nước mới."""
    data = request.get_json() or {}
    try:
        name = clean_name(data.get('name'), 255)
        category = clean_name(data.get('category'), 100)
        try:
            price = int(data.get('price'))
        except (TypeError, ValueError):
            raise OrderError("Giá không hợp lệ.")
        if not 0 <= price <= 10_000_000:
            raise OrderError("Giá phải từ 0 đến 10.000.000đ.")

        with transaction() as cur:
            cur.execute("SELECT id FROM stations WHERE id = %s", (data.get('station_code'),))
            if not cur.fetchone():
                raise OrderError("Hãy chọn trạm bếp.")
            cur.execute("SELECT id FROM alacarte_items WHERE LOWER(name) = LOWER(%s)", (name,))
            if cur.fetchone():
                raise OrderError("Đã có món tên này trong thực đơn gọi lẻ.")
            cur.execute("""INSERT INTO alacarte_items (name, category, station_code, price)
                           VALUES (%s, %s, %s, %s) RETURNING id""",
                        (name, category, data.get('station_code'), price))
            new_id = cur.fetchone()['id']
    except OrderError as e:
        return fail(str(e))
    return jsonify({"success": True, "id": new_id})


@app.route('/api/manager/menu-item/new', methods=['POST'])
def api_manager_menu_item_new():
    """Thêm món buffet mới và gắn vào các gói được chọn."""
    data = request.get_json() or {}
    try:
        name = clean_name(data.get('name'), 150)
        category = clean_name(data.get('category'), 100)
        raw = data.get('package_ids') or []
        try:
            package_ids = sorted({int(x) for x in raw})
        except (TypeError, ValueError):
            raise OrderError("Gói buffet không hợp lệ.")
        if not package_ids:
            raise OrderError("Hãy chọn ít nhất một gói buffet.")

        with transaction() as cur:
            cur.execute("SELECT id FROM stations WHERE id = %s", (data.get('station_id'),))
            if not cur.fetchone():
                raise OrderError("Hãy chọn trạm bếp.")
            cur.execute("SELECT id FROM packages WHERE id = ANY(%s)", (package_ids,))
            if len(cur.fetchall()) != len(package_ids):
                raise OrderError("Có gói buffet không tồn tại.")
            cur.execute("SELECT id FROM menu_items WHERE LOWER(name) = LOWER(%s)", (name,))
            if cur.fetchone():
                raise OrderError("Đã có món buffet tên này.")
            cur.execute("""INSERT INTO menu_items (name, category, station_id)
                           VALUES (%s, %s, %s) RETURNING id""",
                        (name, category, data.get('station_id')))
            new_id = cur.fetchone()['id']
            for pid in package_ids:
                cur.execute("INSERT INTO package_items (package_id, menu_item_id) VALUES (%s, %s)",
                            (pid, new_id))
    except OrderError as e:
        return fail(str(e))
    return jsonify({"success": True, "id": new_id})


@app.route('/api/manager/alacarte/<int:item_id>', methods=['POST'])
def api_manager_alacarte(item_id):
    data = request.get_json() or {}
    sets, params = [], []

    if 'price' in data:
        try:
            price = int(data['price'])
        except (TypeError, ValueError):
            return fail("Giá không hợp lệ.")
        if not 0 <= price <= 10_000_000:
            return fail("Giá phải từ 0 đến 10.000.000đ.")
        sets.append("price = %s"); params.append(price)

    if 'is_active' in data:
        sets.append("is_active = %s"); params.append(bool(data['is_active']))

    if not sets:
        return fail("Không có gì để cập nhật.")

    with transaction() as cur:
        cur.execute(f"UPDATE alacarte_items SET {', '.join(sets)} WHERE id = %s RETURNING id",
                    (*params, item_id))
        if not cur.fetchone():
            return fail("Không tìm thấy món.", 404)
    return jsonify({"success": True})


@app.route('/api/manager/menu-item/<int:item_id>', methods=['POST'])
def api_manager_menu_item(item_id):
    data = request.get_json() or {}
    if 'is_active' not in data:
        return fail("Không có gì để cập nhật.")
    with transaction() as cur:
        cur.execute("UPDATE menu_items SET is_active = %s WHERE id = %s RETURNING id",
                    (bool(data['is_active']), item_id))
        if not cur.fetchone():
            return fail("Không tìm thấy món.", 404)
    return jsonify({"success": True})


# =========================================================
# 9. KIỂM TRA KẾT NỐI DATABASE
# =========================================================

@app.route('/test-db')
def test_db():
    return jsonify({
        "so_ban":      query("SELECT COUNT(*) AS n FROM dining_tables", one=True)["n"],
        "so_nhan_vien": query("SELECT COUNT(*) AS n FROM staffs", one=True)["n"],
        "so_tram":     query("SELECT COUNT(*) AS n FROM stations", one=True)["n"],
        "so_mon":      query("SELECT COUNT(*) AS n FROM menu_items", one=True)["n"],
        "goi_buffet":  [dict(r) for r in query(
            "SELECT p.price, COUNT(pi.menu_item_id) AS so_mon "
            "FROM packages p LEFT JOIN package_items pi ON pi.package_id = p.id "
            "GROUP BY p.price ORDER BY p.price")]
    })


if __name__ == '__main__':
    app.run(debug=True, port=5000)

import os
app.secret_key = os.environ.get('SECRET_KEY', 'gyusachi-do-an-chuyen-nganh')