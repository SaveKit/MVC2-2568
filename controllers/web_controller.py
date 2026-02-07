# controllers/web_controller.py
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
import sqlite3
import random
from datetime import datetime
from models.claim_models import get_claim_model

# สร้าง Blueprint เพื่อทำหน้าที่เป็น Controller แยกส่วนออกมา
web_bp = Blueprint("web", __name__)
DB_PATH = "relief_fund.db"


def get_db_connection():
    """ฟังก์ชันช่วยเชื่อมต่อ Database SQLite"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


@web_bp.route("/login", methods=["GET", "POST"])
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

            # แยกทางเดิน
            # Officer -> หน้า List
            # Citizen -> หน้า Form
            if user["role"] == "officer":
                return redirect(url_for("web.index"))
            else:
                return redirect(url_for("web.create_form"))
        else:
            flash("ชื่อผู้ใช้หรือรหัสผ่านไม่ถูกต้อง", "danger")

    return render_template("login.html")


@web_bp.route("/logout")
def logout():
    """ออกจากระบบ"""
    session.clear()
    return redirect(url_for("web.login"))


@web_bp.route("/")
def index():
    # ถ้ายังไม่ login ให้ไปหน้า login
    if "user" not in session:
        return redirect(url_for("web.login"))

    # ถ้าไม่ใช่ officer ห้ามดูหน้านี้
    if session["role"] != "officer":
        flash("คุณไม่มีสิทธิ์เข้าถึงหน้านี้ (สำหรับเจ้าหน้าที่เท่านั้น)", "warning")
        return redirect(url_for("web.create_form"))

    """Action: แสดงหน้าหลัก (List View)"""
    conn = get_db_connection()
    # Query ข้อมูลมาแสดง
    sql = """
        SELECT c.claim_id, cl.first_name || ' ' || cl.last_name as full_name, 
               cl.income, c.status, comp.amount,
               c.request_date, comp.calc_date
        FROM claims c
        JOIN claimants cl ON c.claimant_id = cl.id
        JOIN compensations comp ON c.claim_id = comp.claim_id
        ORDER BY c.request_date DESC
    """
    rows = conn.execute(sql).fetchall()
    conn.close()

    # ส่งข้อมูลไปยัง View (index.html)
    return render_template("index.html", claims=rows)


@web_bp.route("/create")
def create_form():
    # ถ้ายังไม่ login ให้ไปหน้า login
    if "user" not in session:
        return redirect(url_for("web.login"))

    """Action: แสดงหน้าฟอร์ม (Form View)"""
    return render_template("form.html")


@web_bp.route("/submit", methods=["POST"])
def submit_claim():
    # 1. รับค่า
    first_name = request.form["first_name"]
    last_name = request.form["last_name"]
    income = float(request.form["income"])

    # 2. เชื่อม DB เพื่อดึง Policy
    conn = get_db_connection()
    cursor = conn.cursor()

    # Determine Type & Fetch Policy (ดึงค่า Max Amount จากตาราง policies)
    policy_id = ""
    c_type = ""

    if income < 6500:
        c_type = "LowIncome"
        policy_id = "P01"
    elif income > 50000:
        c_type = "HighIncome"
        policy_id = "P03"
    else:
        c_type = "General"
        policy_id = "P02"

    # ดึงข้อมูล Policy จาก DB
    policy_row = cursor.execute(
        "SELECT max_amount FROM policies WHERE policy_id = ?", (policy_id,)
    ).fetchone()
    policy_limit = policy_row["max_amount"]

    # 3. ส่งค่า Income และ Policy Limit ไปให้ Model คำนวณ
    model = get_claim_model(income, policy_limit)
    compensation_amount = model.calculate_compensation()

    # 4. บันทึกลง Database (เหมือนเดิม)
    cursor.execute(
        "INSERT INTO claimants (first_name, last_name, income, claimant_type) VALUES (?, ?, ?, ?)",
        (first_name, last_name, income, c_type),
    )
    claimant_id = cursor.lastrowid

    claim_id = str(random.randint(10000000, 99999999))
    current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute(
        "INSERT INTO claims (claim_id, claimant_id, request_date, status) VALUES (?, ?, ?, ?)",
        (claim_id, claimant_id, current_date, "Approved"),
    )

    cursor.execute(
        "INSERT INTO compensations (claim_id, amount, calc_date) VALUES (?, ?, ?)",
        (claim_id, compensation_amount, current_date),
    )

    conn.commit()
    conn.close()

    # ส่งข้อความแจ้งเตือน (Flash Message) พร้อมยอดเงิน ไปแสดงที่หน้าถัดไป
    msg = f"✅ บันทึกคำขอสำเร็จ! คุณได้รับเงินเยียวยาจำนวน {compensation_amount:,.2f} บาท"
    flash(msg, "success")

    # 5. กลับไปหน้ารายการคำขอ
    if session.get("role") == "officer":
        # ถ้าเป็นเจ้าหน้าที่ -> ไปหน้ารายการคำขอ
        return redirect(url_for("web.index"))
    else:
        # ถ้าเป็นประชาชน -> กลับมาหน้าเดิม
        return redirect(url_for("web.create_form"))
