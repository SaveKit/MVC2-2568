import sqlite3
import random
from datetime import datetime
from models.claim_models import get_claim_model

DB_PATH = "relief_fund.db"


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def reset_and_seed():
    print("🔄 กำลังล้างข้อมูลเก่าและสร้าง Test Case ใหม่...")
    conn = get_db()
    cursor = conn.cursor()

    # 1. ล้างข้อมูลเก่า
    cursor.execute("DELETE FROM compensations")
    cursor.execute("DELETE FROM claims")
    cursor.execute("DELETE FROM claimants")
    # หมายเหตุ: ไม่ลบ users และ policies

    # 2. เตรียมข้อมูล Test Cases ตามโจทย์
    test_cases = [
        # (ชื่อ, รายได้, คำอธิบายเคส)
        ("นาย รายได้น้อย", 4000, "Low (<6500) -> ได้ 6500"),
        ("นางสาว ทั่วไป", 12000, "General (12000) -> ได้ 12000"),
        ("นาย ทั่วไปเพดาน", 35000, "General (35000) -> ตันที่ 20000"),
        ("ดร. รายได้สูง", 60000, "High (60000/5) -> ได้ 12000"),
        ("คุณหญิง สูงเพดาน", 150000, "High (150000/5) -> ตันที่ 20000"),
    ]

    for name, income, desc in test_cases:
        # A. ดึง Policy Limit จาก DB มาใช้
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

        policy_row = cursor.execute(
            "SELECT max_amount FROM policies WHERE policy_id = ?", (policy_id,)
        ).fetchone()
        policy_limit = policy_row["max_amount"]

        # B. ใช้ Model คำนวณ (Test Logic Model)
        model = get_claim_model(income, policy_limit)
        amount = model.calculate_compensation()

        # C. บันทึกลง DB
        # 1. Claimant
        cursor.execute(
            "INSERT INTO claimants (first_name, last_name, income, claimant_type) VALUES (?, ?, ?, ?)",
            (name, "ทดสอบ", income, c_type),
        )
        claimant_id = cursor.lastrowid

        # 2. Claim
        claim_id = str(random.randint(10000000, 99999999))
        date_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute(
            "INSERT INTO claims (claim_id, claimant_id, request_date, status) VALUES (?, ?, ?, ?)",
            (claim_id, claimant_id, date_str, "Approved"),
        )

        # 3. Compensation
        cursor.execute(
            "INSERT INTO compensations (claim_id, amount, calc_date) VALUES (?, ?, ?)",
            (claim_id, amount, date_str),
        )

        print(f"✅ เพิ่ม: {name} | รายได้ {income:,.0f} | ได้รับ {amount:,.0f} | ({desc})")

    conn.commit()
    conn.close()
    print("\n เสร็จสิ้น! ข้อมูลทดสอบพร้อมใช้งานแล้ว")


if __name__ == "__main__":
    reset_and_seed()
