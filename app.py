import os, json, csv, io
from flask import Flask, render_template, request, redirect, url_for, session, flash, make_response
from flask_socketio import SocketIO, join_room
from dotenv import load_dotenv
from werkzeug.security import check_password_hash
from models import create_tables, get_user_by_username, add_booking, get_bookings, get_booking, set_booking_status
from simulator import start_simulation_for_booking, stop_simulation_for_booking

load_dotenv()
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-change-me')
socketio = SocketIO(app, async_mode='threading', cors_allowed_origins="*")

create_tables()

LANGS = ['th','en']
STRINGS = {
  'th': {
    'brand': 'EverKin',
    'tagline': 'ให้เราดูแลคนที่คุณรัก — บริการรับ-ส่งผู้สูงอายุ พร้อมเพื่อนดูแลร่วมทาง',
    'book_now': 'เริ่มจองบริการ',
    'login': 'เข้าสู่ระบบ',
    'booking_title': 'จองบริการรับ-ส่ง',
    'name': 'ชื่อ-นามสกุล',
    'phone': 'เบอร์โทรศัพท์',
    'pickup': 'สถานที่รับ (Songkhla)',
    'dropoff': 'สถานที่ส่ง (Songkhla)',
    'date': 'วันที่',
    'time': 'เวลา',
    'confirm': 'ยืนยันการจอง',
    'success_title': 'จองสำเร็จ!',
    'success_desc': 'คุณสามารถเปิดหน้าติดตามการเดินทางแบบเรียลไทม์ได้ทันที',
    'go_track': 'ไปหน้าแผนที่ติดตาม',
    'nav_about': 'เกี่ยวกับเรา',
    'nav_pricing': 'ราคา',
    'nav_faq': 'คำถามที่พบบ่อย',
    'nav_contact': 'ติดต่อเรา',
    'switch_lang': 'EN',
    'admin_panel': 'แผงควบคุม',
    'export_csv': 'ส่งออก CSV',
    'logout': 'ออกจากระบบ'
  },
  'en': {
    'brand': 'EverKin',
    'tagline': 'Let us care for your loved ones — Senior transport with a caring buddy.',
    'book_now': 'Book a ride',
    'login': 'Sign in',
    'booking_title': 'Book a service',
    'name': 'Full name',
    'phone': 'Phone number',
    'pickup': 'Pickup (Songkhla)',
    'dropoff': 'Dropoff (Songkhla)',
    'date': 'Date',
    'time': 'Time',
    'confirm': 'Confirm booking',
    'success_title': 'Booked successfully!',
    'success_desc': 'You can track the trip in real time now.',
    'go_track': 'Open live tracking',
    'nav_about': 'About',
    'nav_pricing': 'Pricing',
    'nav_faq': 'FAQ',
    'nav_contact': 'Contact',
    'switch_lang': 'TH',
    'admin_panel': 'Admin panel',
    'export_csv': 'Export CSV',
    'logout': 'Logout'
  }
}

def current_lang():
    lang = request.cookies.get('lang') or session.get('lang','th')
    return lang if lang in LANGS else 'th'

@app.before_request
def handle_lang():
    lang = request.args.get('lang')
    if lang in LANGS:
        session['lang'] = lang

@app.after_request
def set_lang_cookie(resp):
    lang = session.get('lang')
    if lang in LANGS:
        resp.set_cookie('lang', lang, max_age=60*60*24*365)
    return resp

def load_places():
    with open(os.path.join(os.path.dirname(__file__), "data", "seed_places.json"), "r", encoding="utf-8") as f:
        return json.load(f)

@app.context_processor
def inject_common():
    lang = current_lang()
    return {'t': STRINGS[lang], 'LANG': lang}

@app.route('/')
def landing():
    return render_template('landing.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/pricing')
def pricing():
    return render_template('pricing.html')

@app.route('/faq')
def faq():
    return render_template('faq.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/booking', methods=['GET','POST'])
def booking():
    places = load_places()
    if request.method == 'POST':
        name = request.form.get('name','').strip()
        phone = request.form.get('phone','').strip()
        pickup = request.form.get('pickup')
        dropoff = request.form.get('dropoff')
        date = request.form.get('date')
        time = request.form.get('time')
        place_map = {p['name']: p for p in places}
        if pickup not in place_map or dropoff not in place_map:
            flash("กรุณาเลือกจุดรับ/ส่งจากรายการ", "warning")
            return render_template('booking.html', places=places)
        b_id = add_booking({
            'name': name, 'phone': phone,
            'pickup_place': pickup, 'dropoff_place': dropoff,
            'pickup_lat': place_map[pickup]['lat'], 'pickup_lng': place_map[pickup]['lng'],
            'dropoff_lat': place_map[dropoff]['lat'], 'dropoff_lng': place_map[dropoff]['lng'],
            'date': date, 'time': time
        })
        return redirect(url_for('success', booking_id=b_id))
    return render_template('booking.html', places=places)

@app.route('/success/<int:booking_id>')
def success(booking_id):
    b = get_booking(booking_id)
    if not b: return "Not found", 404
    return render_template('success.html', booking=b)

@app.route('/track/<int:booking_id>')
def track(booking_id):
    b = get_booking(booking_id)
    if not b:
        return "Booking not found", 404
    room = f"booking_{booking_id}"
    return render_template('track.html', booking=b, room=room)

@app.route('/admin/login', methods=['GET','POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username','').strip()
        password = request.form.get('password','').strip()
        user = get_user_by_username(username)
        if user and check_password_hash(user['password_hash'], password):
            session['user'] = {'id': user['id'], 'username': user['username'], 'role': user['role']}
            return redirect(url_for('admin_dashboard'))
        flash("ชื่อผู้ใช้หรือรหัสผ่านไม่ถูกต้อง", "danger")
    return render_template('admin_login.html')

@app.route('/admin/logout')
def admin_logout():
    session.pop('user', None)
    return redirect(url_for('admin_login'))

def login_required(role=None):
    def decorator(fn):
        from functools import wraps
        @wraps(fn)
        def wrapper(*args, **kwargs):
            user = session.get('user')
            if not user:
                return redirect(url_for('admin_login'))
            if role and user.get('role') != role:
                return "Forbidden", 403
            return fn(*args, **kwargs)
        return wrapper
    return decorator

@app.route('/admin')
@login_required(role=None)
def admin_dashboard():
    bookings = get_bookings()
    return render_template('admin_dashboard.html', bookings=bookings, user=session.get('user'))

@app.route('/admin/export.csv')
@login_required(role=None)
def admin_export_csv():
    rows = get_bookings()
    out = io.StringIO()
    w = csv.writer(out)
    w.writerow(['id','name','phone','pickup','dropoff','date','time','status','created_at'])
    for r in rows:
        w.writerow([r['id'], r['name'], r['phone'], r['pickup_place'], r['dropoff_place'], r['date'], r['time'], r['status'], r['created_at']])
    resp = make_response(out.getvalue())
    resp.headers['Content-Type'] = 'text/csv; charset=utf-8'
    resp.headers['Content-Disposition'] = 'attachment; filename=everkin_bookings.csv'
    return resp

@app.route('/admin/start/<int:booking_id>', methods=['POST'])
@login_required(role=None)
def admin_start(booking_id):
    b = get_booking(booking_id)
    if not b:
        return "Not found", 404
    ok = start_simulation_for_booking(socketio, booking_id, b['pickup_lat'], b['pickup_lng'], b['dropoff_lat'], b['dropoff_lng'])
    if ok:
        set_booking_status(booking_id, 'in_progress')
        flash("เริ่มจำลองการเดินทางแล้ว", "success")
    else:
        flash("การจำลองกำลังทำงานอยู่", "info")
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/stop/<int:booking_id>', methods=['POST'])
@login_required(role=None)
def admin_stop(booking_id):
    if stop_simulation_for_booking(booking_id):
        set_booking_status(booking_id, 'completed')
        flash("หยุดการจำลองแล้ว", "info")
    return redirect(url_for('admin_dashboard'))

@socketio.on('join', namespace='/tracking')
def on_join(data):
    room = data.get('room')
    if room:
        join_room(room)

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=int(os.getenv('PORT', '5000')))
