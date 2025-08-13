from dotenv import load_dotenv
import os
from models import create_tables, add_user

load_dotenv()
create_tables()
username = os.getenv("ADMIN_USER","admin")
password = os.getenv("ADMIN_PASSWORD","ChangeMe!123")
add_user(username, password, role="admin")
print(f"Admin user ready: {username}")
