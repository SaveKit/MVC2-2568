# controllers/claim_controller.py
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
import random
from datetime import datetime
from utils.db import get_db_connection
from models.claim_models import get_claim_model

# สร้าง Blueprint ชื่อ 'claim'
claim_bp = Blueprint("claim", __name__, template_folder="../templates")


@claim_bp.route("/")
def index():
    # ตรวจสอบสิทธิ์ (ถ้ายังไม่ Login ให้ไปหน้า Login ของ auth)
    if "user" not in session:
        return redirect(url_for("auth.login"))

    # ตรวจสอบ Role (Citizen ห้ามเข้าหน้านี้)
    if session.get("role") != "officer":
        flash("คุณไม่มีสิทธิ์เข้าถึงหน้านี้ (สำหรับเจ้าหน้าที่เท่านั้น)", "warning")
        return redirect(url_for("claim.create_form"))

    """Action: แสดงหน้าหลัก (List View)"""
    conn = get_db_connection()
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
    return render_template("index.html", claims=rows)


@claim_bp.route("/create")
def create_form():
    if "user" not in session:
        return redirect(url_for("auth.login"))

    """Action: แสดงหน้าฟอร์ม (Form View)"""
    return render_template("form.html")


@claim_bp.route("/submit", methods=["POST"])
def submit_claim():
    if "user" not in session:
        return redirect(url_for("auth.login"))

    # รับค่า
    first_name = request.form["first_name"]
    last_name = request.form["last_name"]
    income = float(request.form["income"])

    conn = get_db_connection()
    cursor = conn.cursor()

    # ดึงค่า Max Amount จากตาราง policies
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

    # ส่งค่า Income และ Policy Limit ไปให้ Model คำนวณ
    model = get_claim_model(income, policy_limit)
    compensation_amount = model.calculate_compensation()

    # บันทึกลง Database
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
    flash(
        f"✅ บันทึกคำขอสำเร็จ! คุณได้รับเงินเยียวยาจำนวน {compensation_amount:,.2f} บาท",
        "success",
    )

    # Redirect ตาม Role
    if session.get("role") == "officer":
        return redirect(url_for("claim.index"))
    else:
        return redirect(url_for("claim.create_form"))
