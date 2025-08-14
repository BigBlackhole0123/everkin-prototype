import os
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash
from models import create_tables, add_user

load_dotenv(); create_tables()
username = os.getenv('ADMIN_USER', 'admin')
password = os.getenv('ADMIN_PASSWORD', 'ChangeMe_123!')
if len(password) < 8:
    raise SystemExit('ADMIN_PASSWORD should be at least 8 characters. Edit .env and run again.')
uid = add_user(username, generate_password_hash(password), role='admin')
print(f'✔ Admin user ready: {username} (id={uid})')
