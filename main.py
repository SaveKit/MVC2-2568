# main.py
import os
from flask import Flask
from dotenv import load_dotenv
from database.db_setup import setup_database
from controllers.auth_controller import auth_bp
from controllers.claim_controller import claim_bp

# โหลดตัวแปรแวดล้อมจากไฟล์ .env
load_dotenv()


def create_app():
    """สร้าง Flask App และลงทะเบียน Controller"""
    app = Flask(__name__)

    # ดึงค่าจาก env ถ้าไม่มีให้ใช้ค่า default
    app.secret_key = os.getenv("SECRET_KEY", "fallback_secret_key")

    # ลงทะเบียน Controller (Blueprint)
    app.register_blueprint(auth_bp)
    app.register_blueprint(claim_bp)

    return app


if __name__ == "__main__":
    # เตรียม Database
    setup_database()

    # เริ่มต้น Server
    app = create_app()
    print("Server starting at http://127.0.0.1:5000")
    app.run(debug=True)
