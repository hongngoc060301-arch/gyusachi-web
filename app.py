import csv
import io
import re
import time
from datetime import datetime, timedelta
from pathlib import Path

from flask import Flask, render_template, request, jsonify, redirect, url_for, session, Response, g
from werkzeug.security import generate_password_hash, check_password_hash

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
    rows = query("SELECT id, name, role, avatar FROM staffs WHERE is_active ORDER BY id")
    return [dict(r) for r in rows]


def get_stations():
    # description đổi tên thành "desc" để template (st.desc) dùng như cũ
    rows = query('SELECT id, name, icon, description AS "desc" FROM stations ORDER BY id')
    return [dict(r) for r in rows]


def get_tables(floor=None):
    sql = ("SELECT id, name, capacity, min_capacity, floor, type, status "
           "FROM dining_tables WHERE is_active")
    params = None
    if floor is not None:
        sql += " AND floor = %s"
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
            "SELECT id, name FROM staffs WHERE id = %s AND pin = %s AND is_active",
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
        WHERE t.is_active
        ORDER BY t.floor, (t.type = 'VIP'),
                 NULLIF(regexp_replace(t.id, '\\D', '', 'g'), '')::int, t.id
    """)
    return jsonify({"tables": [dict(r) for r in rows]})


@app.route('/api/packages')
def api_packages():
    """Các gói buffet. today_ok = gói có áp dụng hôm nay không (49K: T2-T5, 69K: T6-CN)."""
    today = datetime.now().isoweekday()          # 1 = thứ 2 ... 7 = chủ nhật
    food, drink = [], []

    for r in query("SELECT id, name, price, valid_days FROM packages WHERE is_active ORDER BY price"):
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
            cur.execute("SELECT id FROM dining_tables WHERE id = %s AND is_active FOR UPDATE", (table_id,))
            if not cur.fetchone():
                raise OrderError("Không tìm thấy bàn.")

            cur.execute("SELECT id FROM orders WHERE table_id = %s AND status = 'OPEN'", (table_id,))
            if cur.fetchone():
                raise OrderError("Bàn này đang có khách, hãy tải lại trang.")

            cur.execute("SELECT id FROM staffs WHERE id = %s AND is_active", (staff_id,))
            if not cur.fetchone():
                raise OrderError("Không tìm thấy nhân viên.")

            if package_id:
                cur.execute("SELECT price FROM packages WHERE id = %s AND is_active", (package_id,))
                p = cur.fetchone()
                if not p or p['price'] < FOOD_PACKAGE_MIN_PRICE:
                    raise OrderError("Gói buffet đồ ăn không hợp lệ.")

            if drink_id:
                cur.execute("SELECT price FROM packages WHERE id = %s AND is_active", (drink_id,))
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
                cur.execute("SELECT price FROM packages WHERE id = %s AND is_active", (package_id,))
                p = cur.fetchone()
                if not p or p['price'] < FOOD_PACKAGE_MIN_PRICE:
                    raise OrderError("Gói buffet đồ ăn không hợp lệ.")

            if drink_id:
                cur.execute("SELECT price, valid_days FROM packages WHERE id = %s AND is_active", (drink_id,))
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


# ---------- Cấu hình chỉnh được ở trang Quản lí (lưu trong bảng app_settings, khoá bắt đầu bằng cfg_) ----------
# Các hằng số phía trên chỉ là GIÁ TRỊ MẶC ĐỊNH; quản lí đổi ở tab "Cấu hình" thì dùng giá trị trong database.

SETTING_KEYS = ('cfg_vat_percent', 'cfg_lunch_end_hour', 'cfg_group_size', 'cfg_dinner_days', 'cfg_holidays')
_SETTINGS_CACHE = {'at': 0.0, 'val': None}


def default_settings():
    return {"vat_percent": VAT_RATE * 100, "lunch_end_hour": LUNCH_END_HOUR, "group_size": GROUP_SIZE,
            "dinner_days": [0, 1, 2, 3],                      # 0 = thứ 2 ... 6 = chủ nhật
            "holidays": sorted(HOLIDAYS_YEARLY | HOLIDAYS_ONCE)}


def get_settings(force=False):
    now = time.time()
    if not force and _SETTINGS_CACHE['val'] is not None and now - _SETTINGS_CACHE['at'] < 5:
        return _SETTINGS_CACHE['val']
    st = default_settings()
    try:
        rows = {r['key']: r['value'] for r in query(
            "SELECT key, value FROM app_settings WHERE key = ANY(%s)", (list(SETTING_KEYS),))}
    except Exception:
        rows = {}                  # chưa chạy file 17 -> dùng mặc định
    try:
        if 'cfg_vat_percent' in rows:     st['vat_percent'] = float(rows['cfg_vat_percent'])
        if 'cfg_lunch_end_hour' in rows:  st['lunch_end_hour'] = int(rows['cfg_lunch_end_hour'])
        if 'cfg_group_size' in rows:      st['group_size'] = int(rows['cfg_group_size'])
        if 'cfg_dinner_days' in rows:
            st['dinner_days'] = sorted({int(x) for x in rows['cfg_dinner_days'].split(',') if x.strip() != ''})
        if 'cfg_holidays' in rows:
            st['holidays'] = sorted({x.strip() for x in rows['cfg_holidays'].split(',') if x.strip()})
    except (TypeError, ValueError):
        st = default_settings()    # dữ liệu hỏng -> quay về mặc định, không làm sập thu ngân
    _SETTINGS_CACHE.update(at=now, val=st)
    return st


def days_label(days):
    """[0,1,2,3] -> 'T2-T5'; [0,2,4] -> 'T2, T4, T6'."""
    names = ['T2', 'T3', 'T4', 'T5', 'T6', 'T7', 'CN']
    d = sorted(days)
    if not d:
        return 'không ngày nào'
    if d == list(range(d[0], d[-1] + 1)) and len(d) > 2:
        return f"{names[d[0]]}-{names[d[-1]]}"
    return ', '.join(names[x] for x in d)


def is_holiday(d):
    h = set(get_settings()['holidays'])
    return d.strftime('%m-%d') in h or d.strftime('%Y-%m-%d') in h


def promo_auto(opened_at):
    """Ưu đãi "đi 4 tính 3" có áp dụng cho bàn mở lúc opened_at không? -> (True/False, lý do)."""
    if isinstance(opened_at, str):
        opened_at = datetime.fromisoformat(opened_at)
    if is_holiday(opened_at.date()):
        return False, "Ngày lễ - không áp dụng đi 4 tính 3"
    st = get_settings()
    promo = f"đi {st['group_size']} tính {st['group_size'] - 1}"
    if opened_at.hour < st['lunch_end_hour']:
        return True, f"Buffet trưa - {promo}"
    if opened_at.weekday() in st['dinner_days']:         # 0 = thứ 2 ... 6 = chủ nhật
        return True, f"Buffet tối {days_label(st['dinner_days'])} - {promo}"
    return False, f"Buffet tối ngoài {days_label(st['dinner_days'])} không áp dụng {promo}"


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
    st = get_settings()
    vat_rate = st['vat_percent'] / 100
    free = guests // st['group_size'] if (apply and food_price) else 0
    discount = free * food_price

    subtotal = food_amount + drink_amount + extra_amount
    taxable = subtotal - discount
    vat = int(round(taxable * vat_rate))

    if free:
        note = f"{auto_reason if promo is None else 'Thu ngân áp dụng ưu đãi nhóm'}: miễn phí {free} suất"
    elif promo is False:
        note = "Thu ngân bỏ ưu đãi nhóm"
    else:
        note = auto_reason

    return {
        "guests": guests,
        "food_name": o['package_name'], "food_price": food_price, "food_amount": food_amount,
        "drink_name": o['drink_name'], "drink_price": drink_price, "drink_amount": drink_amount,
        "lines": lines, "extra_amount": extra_amount,
        "promo_auto": auto_ok, "promo_applied": bool(free), "promo_free": free,
        "promo_note": note, "discount": discount,
        "subtotal": subtotal, "vat_rate": vat_rate, "vat": vat, "total": taxable + vat,
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
    if not check_pw('cashier', pw):
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
        WHERE o.paid_at::date = CURRENT_DATE AND o.voided_at IS NULL
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

PAID = "o.status = 'CLOSED' AND o.paid_at IS NOT NULL AND o.voided_at IS NULL"   # hoá đơn đã thanh toán và chưa bị huỷ


def manager_ok():
    return bool(session.get('manager'))


@app.route('/quanli')
def quanli():
    return render_template('quanli.html')


@app.route('/api/manager/login', methods=['POST'])
def api_manager_login():
    pw = str((request.get_json() or {}).get('password', '')).strip()
    if not check_pw('manager', pw):
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
    all_tables = query("SELECT COUNT(*)::int AS n FROM dining_tables WHERE is_active", one=True)['n']

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
        SELECT CASE WHEN EXTRACT(HOUR FROM o.created_at) < {int(get_settings()['lunch_end_hour'])} THEN 'Trưa' ELSE 'Tối' END AS name,
               COALESCE(SUM(o.total), 0)::bigint AS revenue, COUNT(*)::int AS bills
        FROM orders o WHERE {PAID} AND {rng} GROUP BY 1 ORDER BY 1 DESC""", p)]

    invoices = [dict(r) for r in query(f"""
        SELECT o.id, o.table_id, o.guests, o.payment_method, o.total, o.discount,
               to_char(o.paid_at, 'DD/MM HH24:MI') AS paid_time, COALESCE(pk.name, 'Chỉ gọi lẻ') AS package
        FROM orders o LEFT JOIN packages pk ON pk.id = o.package_id
        WHERE {PAID} AND {rng} ORDER BY o.paid_at DESC LIMIT 300""", p)]

    voided = [dict(r) for r in query("""
        SELECT o.id, o.table_id, o.total, o.void_reason,
               to_char(o.paid_at, 'DD/MM HH24:MI') AS paid_time, to_char(o.voided_at, 'DD/MM HH24:MI') AS voided_time
        FROM orders o
        WHERE o.status = 'CLOSED' AND o.paid_at IS NOT NULL AND o.voided_at IS NOT NULL
          AND o.paid_at::date BETWEEN %s AND %s
        ORDER BY o.voided_at DESC LIMIT 100""", p)]

    return jsonify({"from": d_from, "to": d_to, "summary": s, "by_method": by_method,
                    "by_package": by_package, "by_shift": by_shift,
                    "series": daily_series(d_from, d_to), "invoices": invoices, "voided": voided})


@app.route('/api/manager/invoice/<int:order_id>')
def api_manager_invoice(order_id):
    o = query("""
        SELECT o.id, o.table_id, o.guests, o.payment_method, o.status, o.promo_note,
               to_char(o.created_at, 'DD/MM HH24:MI') AS opened_at,
               to_char(o.paid_at, 'DD/MM HH24:MI') AS paid_at,
               o.food_amount, o.drink_amount, o.extra_amount, o.discount, o.vat_amount, o.total,
               (o.voided_at IS NOT NULL) AS voided, o.void_reason,
               to_char(o.voided_at, 'DD/MM HH24:MI') AS voided_time,
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
    inv = dict(o)
    # Đã thanh toán: đơn giá lấy theo số tiền đã lưu (không đổi dù sau này quản lí sửa giá gói)
    if inv.get('guests') and inv.get('food_amount') is not None:
        inv['package_price'] = inv['food_amount'] // inv['guests']
    if inv.get('guests') and inv.get('drink_amount') is not None:
        inv['drink_price'] = inv['drink_amount'] // inv['guests']
    return jsonify({"success": True, "invoice": inv, "lines": [dict(l) for l in lines]})


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
        SELECT a.id, a.name, a.category, a.station_code AS station, a.price::int AS price, a.is_active,
               EXISTS (SELECT 1 FROM combo_details c WHERE c.combo_id = a.id) AS is_combo
        FROM alacarte_items a ORDER BY a.id""")
    buffet = query("""
        SELECT m.id, m.name, m.category, m.station_id AS station, m.is_active, MIN(p.price)::int AS from_price
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


# ---------- Nhật ký thao tác ----------

def vnd(n):
    return f"{int(n):,}đ".replace(',', '.')


def audit(action, target='', detail=''):
    """Ghi nhật ký. Lỗi ghi nhật ký (VD chưa chạy file 18) không bao giờ làm hỏng thao tác chính."""
    g.audited = True
    try:
        with transaction() as cur:
            cur.execute("INSERT INTO audit_log (actor, action, target, detail) VALUES ('Quản lí', %s, %s, %s)",
                        (str(action)[:100], str(target)[:200], str(detail)[:500]))
    except Exception:
        pass


# ---------- Sửa / xoá món ----------

@app.route('/api/manager/alacarte/<int:item_id>', methods=['POST'])
def api_manager_alacarte(item_id):
    data = request.get_json() or {}
    changes = []
    try:
        with transaction() as cur:
            cur.execute("""SELECT a.id, a.name, a.category, a.station_code, a.price::int AS price, a.is_active,
                                  EXISTS (SELECT 1 FROM combo_details c WHERE c.combo_id = a.id) AS is_combo
                           FROM alacarte_items a WHERE a.id = %s FOR UPDATE""", (item_id,))
            old = cur.fetchone()
            if not old:
                raise OrderError("Không tìm thấy món.")
            sets, params = [], []

            if 'name' in data:
                name = clean_name(data['name'], 255)
                if name != old['name']:
                    cur.execute("SELECT 1 FROM alacarte_items WHERE LOWER(name) = LOWER(%s) AND id <> %s", (name, item_id))
                    if cur.fetchone():
                        raise OrderError("Đã có món gọi lẻ tên này.")
                    sets.append("name = %s"); params.append(name)
                    changes.append(f"tên “{old['name']}” → “{name}”")

            if 'category' in data:
                cat = clean_name(data['category'], 100)
                if cat != old['category']:
                    sets.append("category = %s"); params.append(cat)
                    changes.append(f"nhóm {old['category']} → {cat}")

            if 'station_code' in data and data['station_code'] != old['station_code']:
                if old['is_combo']:
                    raise OrderError("Combo gồm nhiều món con nên không đổi trạm bếp được.")
                cur.execute("SELECT id FROM stations WHERE id = %s", (data['station_code'],))
                if not cur.fetchone():
                    raise OrderError("Trạm bếp không hợp lệ.")
                sets.append("station_code = %s"); params.append(data['station_code'])
                changes.append(f"trạm {old['station_code']} → {data['station_code']}")

            if 'price' in data:
                try:
                    price = int(data['price'])
                except (TypeError, ValueError):
                    raise OrderError("Giá không hợp lệ.")
                if not 0 <= price <= 10_000_000:
                    raise OrderError("Giá phải từ 0 đến 10.000.000đ.")
                if price != old['price']:
                    sets.append("price = %s"); params.append(price)
                    changes.append(f"giá {vnd(old['price'])} → {vnd(price)}")

            if 'is_active' in data and bool(data['is_active']) != old['is_active']:
                sets.append("is_active = %s"); params.append(bool(data['is_active']))
                changes.append("bán lại" if data['is_active'] else "tắt (hết hàng)")

            if not sets:
                if changes or any(k in data for k in ('name', 'category', 'station_code', 'price', 'is_active')):
                    return jsonify({"success": True})       # không có gì thay đổi
                raise OrderError("Không có gì để cập nhật.")
            cur.execute(f"UPDATE alacarte_items SET {', '.join(sets)} WHERE id = %s", (*params, item_id))
    except OrderError as e:
        return fail(str(e))
    audit('Sửa món gọi lẻ', old['name'], '; '.join(changes))
    return jsonify({"success": True})


@app.route('/api/manager/alacarte/<int:item_id>/delete', methods=['POST'])
def api_manager_alacarte_delete(item_id):
    with transaction() as cur:
        cur.execute("SELECT id, name FROM alacarte_items WHERE id = %s FOR UPDATE", (item_id,))
        a = cur.fetchone()
        if not a:
            return fail("Không tìm thấy món.", 404)
        cur.execute("SELECT 1 FROM order_items WHERE name = %s LIMIT 1", (a['name'],))
        if cur.fetchone():
            return fail("Món này đã có lịch sử gọi nên không xoá được (xoá sẽ làm sai báo cáo). Hãy bấm TẮT để ẩn món.")
        cur.execute("DELETE FROM alacarte_items WHERE id = %s", (item_id,))      # combo_details tự xoá theo
    audit('Xoá món gọi lẻ', a['name'])
    return jsonify({"success": True})


@app.route('/api/manager/menu-item/<int:item_id>', methods=['POST'])
def api_manager_menu_item(item_id):
    data = request.get_json() or {}
    changes = []
    try:
        with transaction() as cur:
            cur.execute("SELECT id, name, category, station_id, is_active FROM menu_items WHERE id = %s FOR UPDATE",
                        (item_id,))
            old = cur.fetchone()
            if not old:
                raise OrderError("Không tìm thấy món.")
            sets, params = [], []

            if 'name' in data:
                name = clean_name(data['name'], 150)
                if name != old['name']:
                    cur.execute("SELECT 1 FROM menu_items WHERE LOWER(name) = LOWER(%s) AND id <> %s", (name, item_id))
                    if cur.fetchone():
                        raise OrderError("Đã có món buffet tên này.")
                    sets.append("name = %s"); params.append(name)
                    changes.append(f"tên “{old['name']}” → “{name}”")

            if 'category' in data:
                cat = clean_name(data['category'], 100)
                if cat != old['category']:
                    sets.append("category = %s"); params.append(cat)
                    changes.append(f"nhóm {old['category']} → {cat}")

            if 'station_id' in data and data['station_id'] != old['station_id']:
                cur.execute("SELECT id FROM stations WHERE id = %s", (data['station_id'],))
                if not cur.fetchone():
                    raise OrderError("Trạm bếp không hợp lệ.")
                sets.append("station_id = %s"); params.append(data['station_id'])
                changes.append(f"trạm {old['station_id']} → {data['station_id']}")

            if 'is_active' in data and bool(data['is_active']) != old['is_active']:
                sets.append("is_active = %s"); params.append(bool(data['is_active']))
                changes.append("bán lại" if data['is_active'] else "tắt (hết nguyên liệu)")

            if not sets:
                if any(k in data for k in ('name', 'category', 'station_id', 'is_active')):
                    return jsonify({"success": True})
                raise OrderError("Không có gì để cập nhật.")
            cur.execute(f"UPDATE menu_items SET {', '.join(sets)} WHERE id = %s", (*params, item_id))
    except OrderError as e:
        return fail(str(e))
    audit('Sửa món buffet', old['name'], '; '.join(changes))
    return jsonify({"success": True})


@app.route('/api/manager/menu-item/<int:item_id>/delete', methods=['POST'])
def api_manager_menu_item_delete(item_id):
    with transaction() as cur:
        cur.execute("SELECT id, name FROM menu_items WHERE id = %s FOR UPDATE", (item_id,))
        m = cur.fetchone()
        if not m:
            return fail("Không tìm thấy món.", 404)
        cur.execute("SELECT 1 FROM order_items WHERE menu_item_id = %s LIMIT 1", (item_id,))
        if cur.fetchone():
            return fail("Món này đã có lịch sử gọi nên không xoá được (xoá sẽ làm sai báo cáo). Hãy bấm TẮT để ẩn món.")
        cur.execute("DELETE FROM menu_items WHERE id = %s", (item_id,))          # package_items tự xoá theo
    audit('Xoá món buffet', m['name'])
    return jsonify({"success": True})


# ---------- Huỷ / khôi phục hoá đơn ----------

@app.route('/api/manager/invoice/<int:order_id>/void', methods=['POST'])
def api_manager_invoice_void(order_id):
    reason = ' '.join(str((request.get_json() or {}).get('reason') or '').split())[:300]
    if len(reason) < 3:
        return fail("Hãy nhập lí do huỷ hoá đơn (ít nhất 3 ký tự).")
    with transaction() as cur:
        cur.execute("SELECT id, table_id, total, status, paid_at, voided_at FROM orders WHERE id = %s FOR UPDATE",
                    (order_id,))
        o = cur.fetchone()
        if not o:
            return fail("Không tìm thấy hoá đơn.", 404)
        if o['status'] != 'CLOSED' or not o['paid_at']:
            return fail("Hoá đơn này chưa thanh toán.")
        if o['voided_at']:
            return fail("Hoá đơn này đã được huỷ rồi.")
        cur.execute("UPDATE orders SET voided_at = NOW(), void_reason = %s WHERE id = %s", (reason, order_id))
    audit('Huỷ hoá đơn', f"#{order_id} · bàn {o['table_id']}", f"{vnd(o['total'] or 0)} · lí do: {reason}")
    return jsonify({"success": True})


@app.route('/api/manager/invoice/<int:order_id>/restore', methods=['POST'])
def api_manager_invoice_restore(order_id):
    with transaction() as cur:
        cur.execute("SELECT id, table_id, total, voided_at FROM orders WHERE id = %s FOR UPDATE", (order_id,))
        o = cur.fetchone()
        if not o:
            return fail("Không tìm thấy hoá đơn.", 404)
        if not o['voided_at']:
            return fail("Hoá đơn này chưa bị huỷ.")
        cur.execute("UPDATE orders SET voided_at = NULL, void_reason = NULL WHERE id = %s", (order_id,))
    audit('Khôi phục hoá đơn', f"#{order_id} · bàn {o['table_id']}", vnd(o['total'] or 0))
    return jsonify({"success": True})


# ---------- Xuất báo cáo (CSV mở bằng Excel) ----------

@app.route('/api/manager/export')
def api_manager_export():
    kind = request.args.get('kind', 'invoices')
    d_from, d_to = date_range()
    p = (d_from, d_to)
    buf = io.StringIO()
    buf.write('sep=;\r\n')                       # để Excel (cả máy cài tiếng Việt) tự chia cột
    w = csv.writer(buf, delimiter=';')

    if kind == 'invoices':
        w.writerow(['Mã HĐ', 'Ngày giờ thanh toán', 'Bàn', 'Gói buffet', 'Số khách', 'Tiền buffet đồ ăn',
                    'Tiền buffet nước', 'Gọi lẻ / combo', 'Giảm giá', 'VAT', 'Tổng thanh toán',
                    'Hình thức', 'Ưu đãi', 'Trạng thái', 'Lí do huỷ'])
        rows = query("""
            SELECT o.id, to_char(o.paid_at, 'DD/MM/YYYY HH24:MI') AS paid, o.table_id,
                   COALESCE(pk.name, 'Chỉ gọi lẻ') AS package, o.guests, o.food_amount, o.drink_amount,
                   o.extra_amount, o.discount, o.vat_amount, o.total, o.payment_method, o.promo_note,
                   (o.voided_at IS NOT NULL) AS voided, o.void_reason
            FROM orders o LEFT JOIN packages pk ON pk.id = o.package_id
            WHERE o.status = 'CLOSED' AND o.paid_at IS NOT NULL AND o.paid_at::date BETWEEN %s AND %s
            ORDER BY o.paid_at""", p)
        methods = {'CASH': 'Tiền mặt', 'CARD': 'Thẻ', 'TRANSFER': 'Chuyển khoản'}
        for r in rows:
            w.writerow([r['id'], r['paid'], r['table_id'], r['package'], r['guests'], r['food_amount'] or 0,
                        r['drink_amount'] or 0, r['extra_amount'] or 0, r['discount'] or 0, r['vat_amount'] or 0,
                        r['total'] or 0, methods.get(r['payment_method'], r['payment_method'] or ''),
                        r['promo_note'] or '', 'Đã huỷ' if r['voided'] else 'Đã thanh toán', r['void_reason'] or ''])
    elif kind == 'dishes':
        w.writerow(['Món', 'Nhóm', 'Loại', 'Số lượng', 'Doanh thu'])
        base = f"""FROM order_items oi JOIN orders o ON o.id = oi.order_id
                   WHERE {PAID} AND o.paid_at::date BETWEEN %s AND %s AND oi.status <> 'CANCELLED'"""
        for r in query(f"""SELECT oi.name, SUM(oi.qty)::int AS qty {base} AND oi.kind = 'PACKAGE'
                           GROUP BY oi.name ORDER BY qty DESC, oi.name""", p):
            w.writerow([r['name'], '', 'Món trong buffet', r['qty'], 0])
        for r in query(f"""SELECT oi.name, COALESCE(MAX(a.category), '') AS category, SUM(oi.qty)::int AS qty,
                                  SUM(oi.qty * oi.unit_price)::bigint AS revenue
                           {base} AND oi.parent_id IS NULL AND oi.kind IN ('ALACARTE', 'COMBO')
                           GROUP BY oi.name ORDER BY revenue DESC, oi.name""".replace(
                "FROM order_items oi JOIN orders o ON o.id = oi.order_id",
                "FROM order_items oi JOIN orders o ON o.id = oi.order_id LEFT JOIN alacarte_items a ON a.name = oi.name"), p):
            w.writerow([r['name'], r['category'], 'Gọi lẻ / combo', r['qty'], r['revenue']])
    else:
        return fail("Loại báo cáo không hợp lệ.")

    audit('Xuất báo cáo', 'Hoá đơn' if kind == 'invoices' else 'Thống kê món', f"{d_from} → {d_to}")
    return Response('﻿' + buf.getvalue(), mimetype='text/csv; charset=utf-8',
                    headers={"Content-Disposition": f"attachment; filename=gyusachi_{kind}_{d_from}_{d_to}.csv"})


# ---------- Cấu hình ----------

def parse_holiday(x):
    """'MM-DD' (hằng năm) hoặc 'YYYY-MM-DD' (riêng năm đó) -> chuỗi chuẩn, hoặc báo lỗi."""
    x = str(x).strip()
    try:
        if re.fullmatch(r'\d{2}-\d{2}', x):
            datetime.strptime('2000-' + x, '%Y-%m-%d')          # 2000 là năm nhuận, cho phép 02-29
        elif re.fullmatch(r'\d{4}-\d{2}-\d{2}', x):
            datetime.strptime(x, '%Y-%m-%d')
        else:
            raise ValueError
    except ValueError:
        raise OrderError(f"Ngày lễ “{x}” không hợp lệ (dùng dd/mm hoặc dd/mm/yyyy).")
    return x


@app.route('/api/manager/settings')
def api_manager_settings_get():
    return jsonify({"settings": get_settings(force=True), "defaults": default_settings()})


@app.route('/api/manager/settings', methods=['POST'])
def api_manager_settings_save():
    data = request.get_json() or {}
    try:
        if data.get('reset'):
            new = default_settings()
        else:
            try:
                vat = round(float(data.get('vat_percent')), 2)
                lunch = int(data.get('lunch_end_hour'))
                group = int(data.get('group_size'))
                days = sorted({int(x) for x in (data.get('dinner_days') or [])})
            except (TypeError, ValueError):
                raise OrderError("Giá trị cấu hình không hợp lệ.")
            if not 0 <= vat <= 30:
                raise OrderError("VAT phải từ 0 đến 30%.")
            if not 10 <= lunch <= 20:
                raise OrderError("Giờ kết thúc buổi trưa phải từ 10 đến 20 giờ.")
            if not 2 <= group <= 20:
                raise OrderError("Số người trong nhóm phải từ 2 đến 20.")
            if any(d < 0 or d > 6 for d in days):
                raise OrderError("Ngày áp dụng buổi tối không hợp lệ.")
            hol = sorted({parse_holiday(x) for x in (data.get('holidays') or [])})
            if len(hol) > 300:
                raise OrderError("Danh sách ngày lễ quá dài.")
            new = {"vat_percent": vat, "lunch_end_hour": lunch, "group_size": group,
                   "dinner_days": days, "holidays": hol}

        old = get_settings(force=True)
        with transaction() as cur:
            if data.get('reset'):
                cur.execute("DELETE FROM app_settings WHERE key = ANY(%s)", (list(SETTING_KEYS),))
            else:
                values = {'cfg_vat_percent': str(new['vat_percent']), 'cfg_lunch_end_hour': str(new['lunch_end_hour']),
                          'cfg_group_size': str(new['group_size']),
                          'cfg_dinner_days': ','.join(map(str, new['dinner_days'])),
                          'cfg_holidays': ','.join(new['holidays'])}
                for k, v in values.items():
                    cur.execute("""INSERT INTO app_settings (key, value) VALUES (%s, %s)
                                   ON CONFLICT (key) DO UPDATE SET value = EXCLUDED.value, updated_at = NOW()""", (k, v))
    except OrderError as e:
        return fail(str(e))

    _SETTINGS_CACHE['val'] = None
    ch = []
    if old['vat_percent'] != new['vat_percent']:     ch.append(f"VAT {old['vat_percent']:g}% → {new['vat_percent']:g}%")
    if old['lunch_end_hour'] != new['lunch_end_hour']: ch.append(f"hết buổi trưa {old['lunch_end_hour']}h → {new['lunch_end_hour']}h")
    if old['group_size'] != new['group_size']:       ch.append(f"nhóm {old['group_size']} → {new['group_size']} người")
    if old['dinner_days'] != new['dinner_days']:     ch.append(f"ưu đãi tối {days_label(old['dinner_days'])} → {days_label(new['dinner_days'])}")
    if old['holidays'] != new['holidays']:           ch.append(f"ngày lễ {len(old['holidays'])} → {len(new['holidays'])} ngày")
    audit('Khôi phục cấu hình mặc định' if data.get('reset') else 'Đổi cấu hình', 'Cấu hình', '; '.join(ch) or 'không đổi')
    return jsonify({"success": True, "settings": new})


# ---------- Xem nhật ký + ghi tự động các thao tác quản lí còn lại ----------

@app.route('/api/manager/audit')
def api_manager_audit():
    q = (request.args.get('q') or '').strip()[:100]
    try:
        limit = max(1, min(int(request.args.get('limit') or 200), 500))
    except ValueError:
        limit = 200
    like = f"%{q}%"
    rows = query("""
        SELECT id, to_char(at, 'DD/MM/YYYY HH24:MI:SS') AS at, actor, action, target, detail
        FROM audit_log
        WHERE %s = '' OR action ILIKE %s OR target ILIKE %s OR detail ILIKE %s
        ORDER BY id DESC LIMIT %s""", (q, like, like, like, limit))
    return jsonify({"logs": [dict(r) for r in rows]})


AUDIT_ROUTES = [
    (r'^/api/manager/staff/new$',               'Thêm nhân viên'),
    (r'^/api/manager/staff/[^/]+/delete$',      'Xoá nhân viên'),
    (r'^/api/manager/staff/[^/]+$',             'Sửa nhân viên'),
    (r'^/api/manager/station/[^/]+/pin$',       'Đổi PIN trạm bếp'),
    (r'^/api/manager/password$',                'Đổi mật khẩu'),
    (r'^/api/manager/table/new$',               'Thêm bàn'),
    (r'^/api/manager/table/[^/]+/delete$',      'Xoá bàn'),
    (r'^/api/manager/table/[^/]+$',             'Sửa bàn'),
    (r'^/api/manager/package/\d+$',             'Sửa gói buffet'),
    (r'^/api/manager/alacarte/new$',            'Thêm món gọi lẻ'),
    (r'^/api/manager/menu-item/new$',           'Thêm món buffet'),
    (r'^/api/manager/reservations/new$',        'Nhập đơn đặt bàn'),
]
AUDIT_FIELDS = {'name': 'tên', 'role': 'chức vụ', 'is_active': 'trạng thái', 'price': 'giá', 'days': 'ngày áp dụng',
                'capacity': 'số chỗ', 'min_capacity': 'số chỗ tối thiểu', 'floor': 'tầng', 'type': 'loại',
                'category': 'nhóm', 'avatar': 'ảnh', 'customer_name': 'khách', 'guests': 'số khách',
                'table_id': 'bàn', 'date': 'ngày', 'time': 'giờ', 'id': 'mã', 'package_ids': 'gói',
                'station_code': 'trạm', 'station_id': 'trạm', 'phone': 'SĐT', 'note': 'ghi chú'}
AUDIT_SECRET = {'pin', 'password', 'current', 'new'}


@app.after_request
def audit_manager_changes(resp):
    """Tự ghi nhật ký cho các thao tác quản lí đã thành công mà không có đoạn ghi riêng. Không bao giờ ghi PIN/mật khẩu."""
    try:
        if (request.method != 'POST' or not request.path.startswith('/api/manager/') or getattr(g, 'audited', False)
                or resp.status_code != 200 or not resp.is_json or not (resp.get_json() or {}).get('success')):
            return resp
        for pattern, label in AUDIT_ROUTES:
            if re.match(pattern, request.path):
                body = request.get_json(silent=True) or {}
                parts = []
                for k, v in body.items():
                    if k in AUDIT_SECRET or k == 'which':
                        continue
                    if isinstance(v, bool):
                        v = 'bật' if v else 'tắt'
                    parts.append(f"{AUDIT_FIELDS.get(k, k)}: {v}")
                if any(k in body for k in AUDIT_SECRET - {'password'}) and 'password' not in request.path:
                    parts.append(('đặt mã PIN' if request.path.endswith('/new') else 'đổi mã PIN') if 'pin' in body else '')
                if request.path.endswith('/password'):
                    parts = ['mật khẩu ' + ('thu ngân' if body.get('which') == 'cashier' else 'quản lí')]
                target = 'Mật khẩu' if request.path.endswith('/password') else body.get('name') or body.get('customer_name') or request.path.rstrip('/').split('/')[-2 if request.path.endswith(('/delete', '/pin')) else -1]
                audit(label, target, ', '.join(x for x in parts if x))
                break
    except Exception:
        pass
    return resp


# =========================================================
# 8D. QUẢN LÍ NÂNG CAO: mật khẩu, nhân viên, đặt bàn, bàn, gói buffet
# =========================================================

DEFAULT_PASSWORDS = {'cashier': CASHIER_PASSWORD, 'manager': MANAGER_PASSWORD}


def check_pw(key, pw):
    """Kiểm tra mật khẩu 'cashier' / 'manager'. Đã đổi mật khẩu (bảng app_settings) thì dùng mật khẩu mới,
    chưa đổi thì dùng mật khẩu mặc định trong code."""
    try:
        row = query("SELECT value FROM app_settings WHERE key = %s", (key,), one=True)
    except Exception:
        row = None            # chưa chạy file 17 -> vẫn dùng mật khẩu mặc định
    if row:
        return check_password_hash(row['value'], pw)
    return pw == DEFAULT_PASSWORDS[key]


@app.route('/api/manager/password', methods=['POST'])
def api_manager_password():
    """Đổi mật khẩu thu ngân (chỉ cần đang đăng nhập quản lí) hoặc mật khẩu quản lí (phải nhập mật khẩu hiện tại)."""
    data = request.get_json() or {}
    which = data.get('which')
    new = str(data.get('new') or '').strip()
    if which not in ('cashier', 'manager'):
        return fail("Chọn mật khẩu cần đổi.")
    if which == 'manager' and not check_pw('manager', str(data.get('current') or '').strip()):
        return fail("Mật khẩu quản lí hiện tại không đúng.")
    min_len = 6 if which == 'manager' else 4
    if len(new) < min_len or len(new) > 30:
        return fail(f"Mật khẩu mới phải từ {min_len} đến 30 ký tự.")
    if which == 'cashier' and check_pw('manager', new):
        return fail("Mật khẩu thu ngân không nên trùng mật khẩu quản lí.")
    with transaction() as cur:
        cur.execute("""INSERT INTO app_settings (key, value) VALUES (%s, %s)
                       ON CONFLICT (key) DO UPDATE SET value = EXCLUDED.value, updated_at = NOW()""",
                    (which, generate_password_hash(new)))
    return jsonify({"success": True})


# ---------- Nhân viên ----------

def check_pin(pin):
    pin = str(pin or '').strip()
    if not re.fullmatch(r'\d{4}', pin):
        raise OrderError("Mã PIN phải gồm đúng 4 chữ số.")
    return pin


def pin_taken(cur, pin, except_staff=None, except_station=None):
    cur.execute("SELECT id FROM staffs WHERE pin = %s AND id <> %s", (pin, except_staff or ''))
    if cur.fetchone():
        return True
    cur.execute("SELECT id FROM stations WHERE pin = %s AND id <> %s", (pin, except_station or ''))
    return bool(cur.fetchone())


@app.route('/api/manager/staff')
def api_manager_staff():
    staffs = query("""
        SELECT s.id, s.name, s.role, s.avatar, s.is_active,
               (SELECT COUNT(*) FROM orders o WHERE o.staff_id = s.id)::int AS orders,
               EXISTS (SELECT 1 FROM orders o WHERE o.staff_id = s.id AND o.status = 'OPEN') AS busy
        FROM staffs s ORDER BY s.id""")
    stations = query("SELECT id, name, description FROM stations ORDER BY id")
    return jsonify({"staffs": [dict(r) for r in staffs], "stations": [dict(r) for r in stations]})


@app.route('/api/manager/staff/new', methods=['POST'])
def api_manager_staff_new():
    data = request.get_json() or {}
    try:
        name = clean_name(data.get('name'), 100)
        role = clean_name(data.get('role'), 50)
        pin = check_pin(data.get('pin'))
        avatar = str(data.get('avatar') or '').strip()[:200] or None
        with transaction() as cur:
            if pin_taken(cur, pin):
                raise OrderError("Mã PIN này đã có người dùng, hãy chọn PIN khác.")
            cur.execute("SELECT COALESCE(MAX(id::int), 0) + 1 AS n FROM staffs WHERE id ~ '^[0-9]+$'")
            new_id = '%02d' % cur.fetchone()['n']
            cur.execute("INSERT INTO staffs (id, name, role, pin, avatar) VALUES (%s, %s, %s, %s, %s)",
                        (new_id, name, role, pin, avatar))
    except OrderError as e:
        return fail(str(e))
    return jsonify({"success": True, "id": new_id})


@app.route('/api/manager/staff/<staff_id>', methods=['POST'])
def api_manager_staff_edit(staff_id):
    data = request.get_json() or {}
    try:
        with transaction() as cur:
            cur.execute("SELECT id FROM staffs WHERE id = %s FOR UPDATE", (staff_id,))
            if not cur.fetchone():
                raise OrderError("Không tìm thấy nhân viên.", )
            sets, params = [], []
            if 'name' in data:
                sets.append("name = %s"); params.append(clean_name(data['name'], 100))
            if 'role' in data:
                sets.append("role = %s"); params.append(clean_name(data['role'], 50))
            if 'avatar' in data:
                sets.append("avatar = %s"); params.append(str(data['avatar'] or '').strip()[:200] or None)
            if 'pin' in data:
                pin = check_pin(data['pin'])
                if pin_taken(cur, pin, except_staff=staff_id):
                    raise OrderError("Mã PIN này đã có người dùng, hãy chọn PIN khác.")
                sets.append("pin = %s"); params.append(pin)
            if 'is_active' in data:
                active = bool(data['is_active'])
                if not active:
                    cur.execute("SELECT 1 FROM orders WHERE staff_id = %s AND status = 'OPEN'", (staff_id,))
                    if cur.fetchone():
                        raise OrderError("Nhân viên này đang phụ trách bàn chưa thanh toán, chưa khoá được.")
                sets.append("is_active = %s"); params.append(active)
            if not sets:
                raise OrderError("Không có gì để cập nhật.")
            cur.execute(f"UPDATE staffs SET {', '.join(sets)} WHERE id = %s", (*params, staff_id))
    except OrderError as e:
        return fail(str(e))
    return jsonify({"success": True})


@app.route('/api/manager/staff/<staff_id>/delete', methods=['POST'])
def api_manager_staff_delete(staff_id):
    with transaction() as cur:
        cur.execute("SELECT id FROM staffs WHERE id = %s FOR UPDATE", (staff_id,))
        if not cur.fetchone():
            return fail("Không tìm thấy nhân viên.", 404)
        cur.execute("SELECT 1 FROM orders WHERE staff_id = %s OR cashier_id = %s LIMIT 1", (staff_id, staff_id))
        if cur.fetchone():
            return fail("Nhân viên này đã có lịch sử phục vụ nên không xoá được. Hãy bấm KHOÁ để họ không đăng nhập nữa.")
        cur.execute("DELETE FROM staffs WHERE id = %s", (staff_id,))
    return jsonify({"success": True})


@app.route('/api/manager/station/<station_id>/pin', methods=['POST'])
def api_manager_station_pin(station_id):
    try:
        pin = check_pin((request.get_json() or {}).get('pin'))
        with transaction() as cur:
            cur.execute("SELECT id FROM stations WHERE id = %s FOR UPDATE", (station_id,))
            if not cur.fetchone():
                raise OrderError("Không tìm thấy trạm bếp.")
            if pin_taken(cur, pin, except_station=station_id):
                raise OrderError("Mã PIN này đã có người dùng, hãy chọn PIN khác.")
            cur.execute("UPDATE stations SET pin = %s WHERE id = %s", (pin, station_id))
    except OrderError as e:
        return fail(str(e))
    return jsonify({"success": True})


# ---------- Đặt bàn ----------

RESERVE_FIRST = '10:00'        # giờ đặt sớm nhất
RESERVE_LAST = '21:30'         # giờ đặt muộn nhất
RESERVE_GAP_MIN = 120          # 2 đơn cùng bàn cách nhau tối thiểu 120 phút (bằng thời gian ăn buffet)
RESERVE_MAX_DAYS = 60          # chỉ cho đặt trước tối đa 60 ngày
RESERVE_ACTIVE = ('PENDING', 'CONFIRMED', 'ARRIVED')
RESERVE_FLOW = {               # trạng thái hiện tại -> các trạng thái được chuyển tới
    'PENDING':   ('CONFIRMED', 'CANCELLED'),
    'CONFIRMED': ('ARRIVED', 'NO_SHOW', 'CANCELLED'),
    'ARRIVED':   (),
    'NO_SHOW':   (),
    'CANCELLED': (),
}


def create_reservation(data, source):
    """Kiểm tra + lưu 1 đơn đặt bàn. Dùng chung cho khách tự đặt (WEB) và nhân viên nhập (STAFF).
    Raise OrderError nếu dữ liệu sai."""
    name = clean_name(data.get('customer_name'), 100)
    phone = re.sub(r'[\s.\-]', '', str(data.get('phone') or ''))
    if not re.fullmatch(r'(0\d{9,10}|\+84\d{9,10})', phone):
        raise OrderError("Số điện thoại không hợp lệ.")

    try:
        guests = int(data.get('guests'))
    except (TypeError, ValueError):
        raise OrderError("Số khách không hợp lệ.")
    if not 1 <= guests <= 60:
        raise OrderError("Số khách phải từ 1 đến 60.")

    try:
        day = datetime.strptime(str(data.get('date') or ''), '%Y-%m-%d').date()
        hhmm = datetime.strptime(str(data.get('time') or ''), '%H:%M').strftime('%H:%M')
    except ValueError:
        raise OrderError("Hãy chọn ngày và giờ đặt bàn.")
    now = datetime.now()
    if day < now.date():
        raise OrderError("Ngày đặt bàn không được ở quá khứ.")
    if day > now.date() + timedelta(days=RESERVE_MAX_DAYS):
        raise OrderError(f"Chỉ nhận đặt trước tối đa {RESERVE_MAX_DAYS} ngày.")
    if not RESERVE_FIRST <= hhmm <= RESERVE_LAST:
        raise OrderError(f"Nhà hàng nhận đặt bàn từ {RESERVE_FIRST} đến {RESERVE_LAST}.")
    if day == now.date() and hhmm <= now.strftime('%H:%M'):
        raise OrderError("Giờ đặt bàn đã qua, hãy chọn giờ khác.")

    note = str(data.get('note') or '').strip()[:300] or None
    table_id = str(data.get('table_id') or '').strip()

    with transaction() as cur:
        cur.execute("""SELECT id, name, capacity, min_capacity, type FROM dining_tables
                       WHERE id = %s AND is_active FOR UPDATE""", (table_id,))
        t = cur.fetchone()
        if not t:
            raise OrderError("Không tìm thấy bàn này.")
        if t['type'] == 'VIP':
            if not t['min_capacity'] <= guests <= t['capacity']:
                raise OrderError(f"Phòng VIP nhận từ {t['min_capacity']} đến {t['capacity']} khách.")
        elif guests > t['capacity']:
            raise OrderError(f"Bàn {t['name']} chỉ có {t['capacity']} chỗ.")

        cur.execute("""
            SELECT to_char(reserve_time, 'HH24:MI') AS clash_time FROM reservations
            WHERE table_id = %s AND reserve_date = %s AND status = ANY(%s)
              AND ABS(EXTRACT(EPOCH FROM (reserve_time - %s::time))) / 60 < %s
            LIMIT 1""", (table_id, day, list(RESERVE_ACTIVE), hhmm, RESERVE_GAP_MIN))
        clash = cur.fetchone()
        if clash:
            raise OrderError(f"Bàn {t['name']} đã có người đặt lúc {clash['clash_time']}. Hãy chọn bàn hoặc giờ khác.")

        if source == 'WEB':
            cur.execute("""SELECT COUNT(*)::int AS n FROM reservations
                           WHERE phone = %s AND reserve_date >= CURRENT_DATE
                             AND status IN ('PENDING', 'CONFIRMED')""", (phone,))
            if cur.fetchone()['n'] >= 3:
                raise OrderError("Số điện thoại này đã có 3 đơn đặt bàn sắp tới. Vui lòng liên hệ nhà hàng.")

        cur.execute("""INSERT INTO reservations
                         (customer_name, phone, guests, table_id, reserve_date, reserve_time, note, status, source)
                       VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING id""",
                    (name, phone, guests, table_id, day, hhmm, note,
                     'CONFIRMED' if source == 'STAFF' else 'PENDING', source))
        rid = cur.fetchone()['id']
    return {"id": rid, "table_id": table_id, "table_name": t['name'], "date": str(day), "time": hhmm}


@app.route('/api/book-table', methods=['POST'])
def api_book_table():
    """Khách tự đặt bàn trên website (không cần đăng nhập)."""
    try:
        r = create_reservation(request.get_json() or {}, 'WEB')
    except OrderError as e:
        return fail(str(e))
    return jsonify({"success": True, "reservation": r})


@app.route('/api/manager/reservations')
def api_manager_reservations():
    """Danh sách đặt bàn. Tham số: date_from, date_to (YYYY-MM-DD), status (tuỳ chọn)."""
    d_from = request.args.get('date_from') or str(datetime.now().date())
    d_to = request.args.get('date_to') or d_from
    status = request.args.get('status') or None
    try:
        datetime.strptime(d_from, '%Y-%m-%d'); datetime.strptime(d_to, '%Y-%m-%d')
    except ValueError:
        return fail("Ngày không hợp lệ.")
    rows = query("""
        SELECT r.id, r.customer_name, r.phone, r.guests, r.table_id, t.name AS table_name, t.floor,
               to_char(r.reserve_date, 'YYYY-MM-DD') AS date, to_char(r.reserve_time, 'HH24:MI') AS time,
               r.note, r.status, r.source, to_char(r.created_at, 'DD/MM HH24:MI') AS created
        FROM reservations r JOIN dining_tables t ON t.id = r.table_id
        WHERE r.reserve_date BETWEEN %s AND %s AND (%s::text IS NULL OR r.status = %s)
        ORDER BY r.reserve_date, r.reserve_time, r.id""", (d_from, d_to, status, status))
    out = [dict(r) for r in rows]
    for r in out:
        r['next'] = list(RESERVE_FLOW.get(r['status'], ()))
    counts = {}
    for r in out:
        counts[r['status']] = counts.get(r['status'], 0) + 1
    return jsonify({"reservations": out, "counts": counts,
                    "tables": [dict(t) for t in query(
                        "SELECT id, name, floor, capacity, min_capacity, type FROM dining_tables "
                        "WHERE is_active ORDER BY floor, (type = 'VIP'), "
                        "NULLIF(regexp_replace(id, '\\D', '', 'g'), '')::int, id")]})


@app.route('/api/manager/reservations/new', methods=['POST'])
def api_manager_reservation_new():
    """Nhân viên nhập đơn đặt bàn (khách gọi điện) - tự xác nhận."""
    try:
        r = create_reservation(request.get_json() or {}, 'STAFF')
    except OrderError as e:
        return fail(str(e))
    return jsonify({"success": True, "reservation": r})


@app.route('/api/manager/reservations/<int:rid>/status', methods=['POST'])
def api_manager_reservation_status(rid):
    new = (request.get_json() or {}).get('status')
    with transaction() as cur:
        cur.execute("SELECT status FROM reservations WHERE id = %s FOR UPDATE", (rid,))
        r = cur.fetchone()
        if not r:
            return fail("Không tìm thấy đơn đặt bàn.", 404)
        if new not in RESERVE_FLOW.get(r['status'], ()):
            return fail("Không chuyển được sang trạng thái này.")
        cur.execute("UPDATE reservations SET status = %s, updated_at = NOW() WHERE id = %s", (new, rid))
    return jsonify({"success": True})


# ---------- Bàn ----------

TABLE_FLOORS = (1, 2)
NATURAL_TABLE_ORDER = ("t.floor, (t.type = 'VIP'), "
                       "NULLIF(regexp_replace(t.id, '\\D', '', 'g'), '')::int, t.id")


def table_fields(data, partial=False):
    """Đọc + kiểm tra thông tin bàn. partial=True: chỉ kiểm tra các trường có gửi lên."""
    out = {}
    if 'name' in data or not partial:
        out['name'] = clean_name(data.get('name'), 50)
    if 'capacity' in data or not partial:
        try:
            out['capacity'] = int(data.get('capacity'))
        except (TypeError, ValueError):
            raise OrderError("Số chỗ không hợp lệ.")
        if not 1 <= out['capacity'] <= 30:
            raise OrderError("Số chỗ phải từ 1 đến 30.")
    if 'min_capacity' in data or not partial:
        try:
            out['min_capacity'] = int(data.get('min_capacity') or 1)
        except (TypeError, ValueError):
            raise OrderError("Số khách tối thiểu không hợp lệ.")
        if out['min_capacity'] < 1:
            raise OrderError("Số khách tối thiểu phải từ 1.")
    if 'floor' in data or not partial:
        try:
            out['floor'] = int(data.get('floor'))
        except (TypeError, ValueError):
            raise OrderError("Tầng không hợp lệ.")
        if out['floor'] not in TABLE_FLOORS:
            raise OrderError("Nhà hàng có tầng 1 và tầng 2.")
    if 'type' in data or not partial:
        out['type'] = str(data.get('type') or 'NORMAL').upper()
        if out['type'] not in ('NORMAL', 'VIP'):
            raise OrderError("Loại bàn không hợp lệ.")
    return out


@app.route('/api/manager/tables')
def api_manager_tables():
    rows = query(f"""
        SELECT t.id, t.name, t.capacity, t.min_capacity, t.floor, t.type, t.is_active,
               EXISTS (SELECT 1 FROM orders o WHERE o.table_id = t.id AND o.status = 'OPEN') AS busy,
               (SELECT COUNT(*) FROM orders o WHERE o.table_id = t.id)::int AS orders,
               (SELECT COUNT(*) FROM reservations r WHERE r.table_id = t.id
                  AND r.reserve_date >= CURRENT_DATE AND r.status IN ('PENDING', 'CONFIRMED'))::int AS upcoming
        FROM dining_tables t ORDER BY {NATURAL_TABLE_ORDER}""")
    return jsonify({"tables": [dict(r) for r in rows]})


@app.route('/api/manager/table/new', methods=['POST'])
def api_manager_table_new():
    data = request.get_json() or {}
    try:
        tid = re.sub(r'\s', '', str(data.get('id') or '')).upper()
        if not re.fullmatch(r'[A-Z0-9]{1,10}', tid):
            raise OrderError("Mã bàn chỉ gồm chữ và số, tối đa 10 ký tự (VD: B12).")
        f = table_fields({**data, 'name': data.get('name') or tid})
        if f['min_capacity'] > f['capacity']:
            raise OrderError("Số khách tối thiểu không được lớn hơn số chỗ.")
        with transaction() as cur:
            cur.execute("SELECT 1 FROM dining_tables WHERE id = %s", (tid,))
            if cur.fetchone():
                raise OrderError("Mã bàn này đã tồn tại.")
            cur.execute("""INSERT INTO dining_tables (id, name, capacity, min_capacity, floor, type)
                           VALUES (%s, %s, %s, %s, %s, %s)""",
                        (tid, f['name'], f['capacity'], f['min_capacity'], f['floor'], f['type']))
    except OrderError as e:
        return fail(str(e))
    return jsonify({"success": True, "id": tid})


@app.route('/api/manager/table/<table_id>', methods=['POST'])
def api_manager_table_edit(table_id):
    data = request.get_json() or {}
    try:
        f = table_fields(data, partial=True)
        with transaction() as cur:
            cur.execute("SELECT * FROM dining_tables WHERE id = %s FOR UPDATE", (table_id,))
            t = cur.fetchone()
            if not t:
                raise OrderError("Không tìm thấy bàn.")
            cap = f.get('capacity', t['capacity'])
            mn = f.get('min_capacity', t['min_capacity'])
            if mn > cap:
                raise OrderError("Số khách tối thiểu không được lớn hơn số chỗ.")

            cur.execute("SELECT 1 FROM orders WHERE table_id = %s AND status = 'OPEN'", (table_id,))
            busy = bool(cur.fetchone())
            if busy and ('floor' in f and f['floor'] != t['floor']):
                raise OrderError("Bàn đang có khách, chưa đổi tầng được.")

            sets, params = [], []
            for k, v in f.items():
                sets.append(f"{k} = %s"); params.append(v)
            if 'is_active' in data:
                active = bool(data['is_active'])
                if not active:
                    if busy:
                        raise OrderError("Bàn đang có khách, chưa ẩn được.")
                    cur.execute("""SELECT COUNT(*)::int AS n FROM reservations WHERE table_id = %s
                                   AND reserve_date >= CURRENT_DATE AND status IN ('PENDING', 'CONFIRMED')""",
                                (table_id,))
                    n = cur.fetchone()['n']
                    if n:
                        raise OrderError(f"Bàn đang có {n} đơn đặt sắp tới, hãy xử lí các đơn đó trước.")
                sets.append("is_active = %s"); params.append(active)
            if not sets:
                raise OrderError("Không có gì để cập nhật.")
            cur.execute(f"UPDATE dining_tables SET {', '.join(sets)} WHERE id = %s", (*params, table_id))
    except OrderError as e:
        return fail(str(e))
    return jsonify({"success": True})


@app.route('/api/manager/table/<table_id>/delete', methods=['POST'])
def api_manager_table_delete(table_id):
    with transaction() as cur:
        cur.execute("SELECT id FROM dining_tables WHERE id = %s FOR UPDATE", (table_id,))
        if not cur.fetchone():
            return fail("Không tìm thấy bàn.", 404)
        cur.execute("""SELECT (SELECT COUNT(*) FROM orders WHERE table_id = %s)
                        + (SELECT COUNT(*) FROM reservations WHERE table_id = %s) AS n""", (table_id, table_id))
        if cur.fetchone()['n']:
            return fail("Bàn này đã có lịch sử hoá đơn hoặc đặt bàn nên không xoá được. Hãy bấm ẨN.")
        cur.execute("DELETE FROM dining_tables WHERE id = %s", (table_id,))
    return jsonify({"success": True})


# ---------- Gói buffet ----------

@app.route('/api/manager/packages')
def api_manager_packages():
    rows = query("""
        SELECT p.id, p.name, p.price, p.valid_days, p.is_active,
               (SELECT COUNT(*) FROM package_items pi WHERE pi.package_id = p.id)::int AS items,
               (SELECT COUNT(*) FROM orders o WHERE o.status = 'OPEN'
                  AND (o.package_id = p.id OR o.drink_package_id = p.id))::int AS open_orders
        FROM packages p ORDER BY p.price""")
    out = []
    for r in rows:
        r = dict(r)
        r['days'] = [int(x) for x in (r.pop('valid_days') or '').split(',') if x.strip()]
        r['kind'] = 'food' if r['price'] >= FOOD_PACKAGE_MIN_PRICE else 'drink'
        out.append(r)
    return jsonify({"packages": out, "food_min": FOOD_PACKAGE_MIN_PRICE})


@app.route('/api/manager/package/<int:pid>', methods=['POST'])
def api_manager_package(pid):
    data = request.get_json() or {}
    try:
        with transaction() as cur:
            cur.execute("SELECT * FROM packages WHERE id = %s FOR UPDATE", (pid,))
            p = cur.fetchone()
            if not p:
                raise OrderError("Không tìm thấy gói.")
            sets, params = [], []

            if 'name' in data:
                sets.append("name = %s"); params.append(clean_name(data['name'], 100))

            if 'price' in data:
                try:
                    price = int(data['price'])
                except (TypeError, ValueError):
                    raise OrderError("Giá không hợp lệ.")
                if not 1000 <= price <= 5_000_000:
                    raise OrderError("Giá gói phải từ 1.000đ đến 5.000.000đ.")
                if (price >= FOOD_PACKAGE_MIN_PRICE) != (p['price'] >= FOOD_PACKAGE_MIN_PRICE):
                    raise OrderError("Gói đồ ăn phải từ %s trở lên, gói nước phải dưới mức đó."
                                     % f"{FOOD_PACKAGE_MIN_PRICE:,}đ".replace(',', '.'))
                cur.execute("SELECT 1 FROM packages WHERE price = %s AND id <> %s", (price, pid))
                if cur.fetchone():
                    raise OrderError("Đã có gói khác cùng mức giá này.")
                sets.append("price = %s"); params.append(price)

            if 'days' in data:
                raw = data['days'] or []
                try:
                    days = sorted({int(x) for x in raw})
                except (TypeError, ValueError):
                    raise OrderError("Ngày áp dụng không hợp lệ.")
                if any(d < 1 or d > 7 for d in days):
                    raise OrderError("Ngày áp dụng không hợp lệ.")
                # không chọn ngày nào hoặc chọn cả 7 ngày = áp dụng mọi ngày
                sets.append("valid_days = %s")
                params.append(None if not days or len(days) == 7 else ','.join(map(str, days)))

            if 'is_active' in data:
                active = bool(data['is_active'])
                if not active:
                    cur.execute("""SELECT COUNT(*)::int AS n FROM orders WHERE status = 'OPEN'
                                   AND (package_id = %s OR drink_package_id = %s)""", (pid, pid))
                    n = cur.fetchone()['n']
                    if n:
                        raise OrderError(f"Đang có {n} bàn dùng gói này, chưa tắt được.")
                sets.append("is_active = %s"); params.append(active)

            if not sets:
                raise OrderError("Không có gì để cập nhật.")
            cur.execute(f"UPDATE packages SET {', '.join(sets)} WHERE id = %s", (*params, pid))
    except OrderError as e:
        return fail(str(e))
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
