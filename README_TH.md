# EverKin — Prototype v0.3 (Songkhla Pilot)
**ไฟล์ครบ & แก้บั๊ก พร้อม Deploy**

## Run Local
```
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python create_admin.py
python app.py
```
เปิดเว็บ: http://localhost:5000  (Admin: /admin/login)

## Render Deploy
- Build: `pip install -r requirements.txt`
- Start: `python app.py`
