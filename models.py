import os, sqlite3, threading
from contextlib import closing

DB_PATH = os.path.join(os.path.dirname(__file__), 'everkin.db')
_lock = threading.Lock()

def get_conn():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def create_tables():
    schema_path = os.path.join(os.path.dirname(__file__), 'schema.sql')
    with closing(get_conn()) as conn, open(schema_path, 'r', encoding='utf-8') as f:
        conn.executescript(f.read()); conn.commit()

def add_user(username, password_hash, role='admin'):
    with _lock, closing(get_conn()) as conn:
        cur = conn.execute(
            "INSERT OR REPLACE INTO users (username, password_hash, role) VALUES (?, ?, COALESCE((SELECT role FROM users WHERE username=?),'admin'))",
            (username, password_hash, username)
        ); conn.commit(); return cur.lastrowid

def get_user_by_username(username):
    with closing(get_conn()) as conn:
        cur = conn.execute('SELECT * FROM users WHERE username=?', (username,))
        r = cur.fetchone(); return dict(r) if r else None

def add_booking(data):
    with _lock, closing(get_conn()) as conn:
        cur = conn.execute(
            """
            INSERT INTO bookings (name, phone, pickup_place, dropoff_place, pickup_lat, pickup_lng, dropoff_lat, dropoff_lng, date, time, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'pending')
            """,
            (
                data['name'], data['phone'],
                data['pickup_place'], data['dropoff_place'],
                data['pickup_lat'], data['pickup_lng'],
                data['dropoff_lat'], data['dropoff_lng'],
                data['date'], data['time']
            )
        ); conn.commit(); return cur.lastrowid

def get_bookings():
    with closing(get_conn()) as conn:
        cur = conn.execute('SELECT * FROM bookings ORDER BY created_at DESC')
        return [dict(r) for r in cur.fetchall()]

def get_booking(booking_id:int):
    with closing(get_conn()) as conn:
        cur = conn.execute('SELECT * FROM bookings WHERE id=?', (booking_id,))
        r = cur.fetchone(); return dict(r) if r else None

def set_booking_status(booking_id:int, status:str):
    with _lock, closing(get_conn()) as conn:
        conn.execute('UPDATE bookings SET status=? WHERE id=?', (status, booking_id)); conn.commit()
