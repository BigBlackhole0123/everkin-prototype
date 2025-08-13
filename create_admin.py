
import os
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash
from models import create_tables, user_exists, add_user

load_dotenv()
create_tables()

def create_user_from_env(prefix, role):
    user = os.getenv(f"{prefix}_USER")
    pwd = os.getenv(f"{prefix}_PASSWORD")
    if not user or not pwd:
        print(f"Skip {role}: please set {prefix}_USER and {prefix}_PASSWORD in .env")
        return
    if user_exists(user):
        print(f"{role} user '{user}' already exists. Skipping.")
        return
    add_user(user, generate_password_hash(pwd), role)
    print(f"Created {role} user '{user}'")

if __name__ == "__main__":
    create_user_from_env("ADMIN", "admin")
    create_user_from_env("BOARD", "board")
    print("Done.")
