# controllers/auth_controller.py
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from utils.db import get_db_connection

# สร้าง Blueprint ชื่อ 'auth'
auth_bp = Blueprint("auth", __name__, template_folder="../templates")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    """จัดการการเข้าสู่ระบบ"""
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = get_db_connection()
        user = conn.execute(
            "SELECT * FROM users WHERE username = ?", (username,)
        ).fetchone()
        conn.close()

        if user and user["password"] == password:
            session["user"] = user["username"]
            session["role"] = user["role"]

            # Login สำเร็จ -> แยกทางเดินตาม Role
            # Officer -> หน้า List
            # Citizen -> หน้า Form
            if user["role"] == "officer":
                return redirect(url_for("claim.index"))
            else:
                return redirect(url_for("claim.create_form"))
        else:
            flash("ชื่อผู้ใช้หรือรหัสผ่านไม่ถูกต้อง", "danger")

    return render_template("login.html")


@auth_bp.route("/logout")
def logout():
    """ออกจากระบบ"""
    session.clear()
    return redirect(url_for("auth.login"))
