# main.py
from flask import Flask
from database.db_setup import setup_database
from controllers.auth_controller import auth_bp
from controllers.claim_controller import claim_bp


def create_app():
    """สร้าง Flask App และลงทะเบียน Controller"""
    app = Flask(__name__)

    # Secret key จำเป็นสำหรับการทำงานบางอย่างของ Flask
    app.secret_key = "exam_secret_key_123"

    # ลงทะเบียน Controller (Blueprint)
    app.register_blueprint(auth_bp)
    app.register_blueprint(claim_bp)

    return app


if __name__ == "__main__":
    # 1. เตรียม Database
    setup_database()

    # 2. เริ่มต้น Server
    app = create_app()
    print("Server starting at http://127.0.0.1:5000")
    app.run(debug=True)
