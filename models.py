
import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "everkin.db")

def get_db():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def create_tables():
    with open(os.path.join(os.path.dirname(__file__), "schema.sql"), "r", encoding="utf-8") as f:
        schema = f.read()
    conn = get_db()
    conn.executescript(schema)
    conn.commit()
    conn.close()

def user_exists(username):
    conn = get_db()
    cur = conn.execute("SELECT id FROM users WHERE username=?", (username,))
    row = cur.fetchone()
    conn.close()
    return row is not None

def add_user(username, password_hash, role):
    conn = get_db()
    conn.execute("INSERT INTO users (username, password_hash, role) VALUES (?,?,?)",
                 (username, password_hash, role))
    conn.commit()
    conn.close()

def get_user_by_username(username):
    conn = get_db()
    cur = conn.execute("SELECT * FROM users WHERE username=?", (username,))
    row = cur.fetchone()
    conn.close()
    return row

def add_booking(data):
    conn = get_db()
    cur = conn.execute(
        """INSERT INTO bookings 
        (name, phone, pickup_place, dropoff_place, pickup_lat, pickup_lng, dropoff_lat, dropoff_lng, date, time, status)
        VALUES (?,?,?,?,?,?,?,?,?,?,?)""" ,
        (data['name'], data['phone'], data['pickup_place'], data['dropoff_place'], data['pickup_lat'], data['pickup_lng'],
         data['dropoff_lat'], data['dropoff_lng'], data['date'], data['time'], 'pending')
    )
    conn.commit()
    booking_id = cur.lastrowid
    conn.close()
    return booking_id

def get_bookings():
    conn = get_db()
    cur = conn.execute("SELECT * FROM bookings ORDER BY created_at DESC")
    rows = cur.fetchall()
    conn.close()
    return rows

def get_booking(booking_id):
    conn = get_db()
    cur = conn.execute("SELECT * FROM bookings WHERE id=?", (booking_id,))
    row = cur.fetchone()
    conn.close()
    return row

def set_booking_status(booking_id, status):
    conn = get_db()
    conn.execute("UPDATE bookings SET status=? WHERE id=?", (status, booking_id))
    conn.commit()
    conn.close()
