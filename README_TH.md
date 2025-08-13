
# EverKin — Prototype (Songkhla Pilot)

Prototype นี้พร้อมให้รัน **ทันที**: จองบริการ → Admin เริ่มจำลอง → หน้าติดตามแผนที่ (Leaflet + SocketIO)

## 1) เตรียมเครื่อง
- ติดตั้ง Python 3.10+
- รันคำสั่งด้านล่างในโฟลเดอร์โปรเจกต์

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate

pip install -r requirements.txt
cp .env.example .env
# แก้ไฟล์ .env ใส่รหัสผู้ใช้
python create_admin.py
python app.py
```

เปิดเบราว์เซอร์ไปที่: http://localhost:5000

- หน้า Admin: http://localhost:5000/admin/login

## 2) วิธีใช้งาน
1. เข้าแท็บ **จองบริการ** เลือกจุดรับ-ส่งในสงขลา ระบุวันเวลา → ยืนยัน
2. ระบบจะพาไปหน้า **ติดตาม (Track)** ของการจองนั้น
3. เปิดแท็บใหม่ → ไปที่ **/admin/login** → เข้าด้วยบัญชีที่คุณสร้างจาก `.env`
4. ใน **Dashboard** กด **เริ่มจำลอง** ที่ booking นั้น → กลับไปดูหน้า Track จะเห็นรถวิ่งบนแผนที่แบบเรียลไทม์
5. กด **หยุด** เพื่อจบการจำลอง (สถานะจะเป็น completed)

## 3) Docker (ทางเลือก)
```bash
docker compose up --build
# เปิด http://localhost:5000
```

> ก่อน `docker compose up`, แก้ไฟล์ `.env` ให้เรียบร้อย และสร้างผู้ใช้ด้วย:
> ```bash
> docker run --rm -v "$PWD":/app -w /app python:3.11-slim bash -lc "pip install -r requirements.txt && python create_admin.py"
> ```

## 4) Deploy Guide (Render/Railway)
- Render:
  - สร้าง Web Service จาก Git หรืออัปโหลดโค้ด (ใช้ `Dockerfile` นี้ได้เลย)
  - **Env Vars** ที่ต้องตั้ง: `SECRET_KEY`, `ADMIN_USER`, `ADMIN_PASSWORD`, (ถ้าต้องการ) `BOARD_USER`, `BOARD_PASSWORD`
  - Start Command: `python app.py`
- Railway: คล้ายกัน ตั้งค่า env และ start command

## 5) ค่าเริ่มต้น / ความปลอดภัย
- ไฟล์ `.env.example` มีรูปแบบตัวแปรที่ต้องใช้ (อย่า commit `.env`)
- ผู้ใช้จะถูกเก็บเป็น hash ในฐานข้อมูล SQLite ด้วย `create_admin.py`

## โครงสร้างโฟลเดอร์
```
everkin_prototype/
  app.py
  models.py
  simulator.py
  create_admin.py
  schema.sql
  data/seed_places.json
  templates/
    base.html, landing.html, booking.html, admin_login.html, admin_dashboard.html, track.html
  static/css/styles.css
  requirements.txt
  Dockerfile
  docker-compose.yml
  .env.example
  README_TH.md
```

หากติดปัญหา เปิด issue: ตรวจ log ใน console ที่รัน `python app.py` แล้วส่งข้อความ error มาได้เลย
