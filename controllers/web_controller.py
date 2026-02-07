# controllers/web_controller.py
from flask import Blueprint, render_template, request, redirect, url_for, flash
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


@web_bp.route("/")
def index():
    """Action: แสดงหน้าหลัก (List View)"""
    conn = get_db_connection()
    # Query ข้อมูลมาแสดง
    sql = """
        SELECT c.claim_id, cl.first_name || ' ' || cl.last_name as full_name, 
               cl.income, c.status, comp.amount
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
    """Action: แสดงหน้าฟอร์ม (Form View)"""
    return render_template("form.html")


@web_bp.route("/submit", methods=["POST"])
def submit_claim():
    """Action: รับค่าจากฟอร์ม -> คำนวณ (Model) -> บันทึก -> กลับหน้าหลัก"""
    # 1. รับค่าจาก View
    first_name = request.form["first_name"]
    last_name = request.form["last_name"]
    income = float(request.form["income"])

    # 2. เรียกใช้ Model เพื่อคำนวณ (Business Logic)
    model = get_claim_model(income)
    compensation_amount = model.calculate_compensation()

    # Determine Type
    c_type = "General"
    if income < 6500:
        c_type = "LowIncome"
    elif income > 50000:
        c_type = "HighIncome"

    # 3. บันทึกลง Database
    conn = get_db_connection()
    cursor = conn.cursor()

    # Insert Claimant
    cursor.execute(
        "INSERT INTO claimants (first_name, last_name, income, claimant_type) VALUES (?, ?, ?, ?)",
        (first_name, last_name, income, c_type),
    )
    claimant_id = cursor.lastrowid

    # Generate IDs & Date
    claim_id = str(random.randint(10000000, 99999999))
    current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Insert Claim
    cursor.execute(
        "INSERT INTO claims (claim_id, claimant_id, request_date, status) VALUES (?, ?, ?, ?)",
        (claim_id, claimant_id, current_date, "Approved"),
    )

    # Insert Compensation
    cursor.execute(
        "INSERT INTO compensations (claim_id, amount, calc_date) VALUES (?, ?, ?)",
        (claim_id, compensation_amount, current_date),
    )

    conn.commit()
    conn.close()

    # 4. ส่งผลลัพธ์กลับไปหน้าหลัก (Redirect)
    return redirect(url_for("web.index"))
