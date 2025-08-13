import os, sqlite3
from werkzeug.security import generate_password_hash

DB_PATH = os.path.join(os.path.dirname(__file__), "everkin.db")

def connect():
    con = sqlite3.connect(DB_PATH, check_same_thread=False)
    con.row_factory = sqlite3.Row
    return con

def create_tables():
    con = connect()
    cur = con.cursor()
    with open(os.path.join(os.path.dirname(__file__), "schema.sql"), "r", encoding="utf-8") as f:
        cur.executescript(f.read())
    con.commit()
    con.close()

def get_user_by_username(username):
    con = connect()
    cur = con.cursor()
    cur.execute("SELECT * FROM users WHERE username=?", (username,))
    row = cur.fetchone()
    con.close()
    return dict(row) if row else None

def add_user(username, password, role="admin"):
    con = connect()
    cur = con.cursor()
    cur.execute(
        "INSERT OR REPLACE INTO users(username, password_hash, role) VALUES (?,?,?)",
        (username, generate_password_hash(password), role),
    )
    con.commit()
    con.close()

def add_booking(data: dict) -> int:
    con = connect()
    cur = con.cursor()
    cur.execute(
        """
        INSERT INTO bookings
        (name, phone, pickup_place, dropoff_place, pickup_lat, pickup_lng, dropoff_lat, dropoff_lng, date, time)
        VALUES (?,?,?,?,?,?,?,?,?,?)
        """",
        (
            data['name'],
            data['phone'],
            data['pickup_place'],
            data['dropoff_place'],
            data['pickup_lat'],
            data['pickup_lng'],
            data['dropoff_lat'],
            data['dropoff_lng'],
            data['date'],
            data['time'],
        ),
    )
    con.commit()
    bid = cur.lastrowid
    con.close()
    return bid

def get_bookings():
    con = connect()
    cur = con.cursor()
    cur.execute("SELECT * FROM bookings ORDER BY created_at DESC, id DESC")
    rows = [dict(r) for r in cur.fetchall()]
    con.close()
    return rows

def get_booking(booking_id: int):
    con = connect()
    cur = con.cursor()
    cur.execute("SELECT * FROM bookings WHERE id=?", (booking_id,))
    row = cur.fetchone()
    con.close()
    return dict(row) if row else None

def set_booking_status(booking_id: int, status: str):
    con = connect()
    cur = con.cursor()
    cur.execute("UPDATE bookings SET status=? WHERE id=?", (status, booking_id))
    con.commit()
    con.close()
