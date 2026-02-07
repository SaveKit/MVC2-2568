# database/db_setup.py
import sqlite3


def create_connection():
    """สร้างการเชื่อมต่อกับฐานข้อมูล SQLite"""
    conn = sqlite3.connect("relief_fund.db")
    return conn


def setup_database():
    """สร้างตารางตามที่โจทย์กำหนด"""
    conn = create_connection()
    cursor = conn.cursor()

    # 1. ตาราง Claimants (ผู้ขอเยียวยา)
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS claimants (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            income REAL NOT NULL,
            claimant_type TEXT NOT NULL
        )
    """
    )

    # 2. ตาราง Policies (นโยบายการเยียวยา)
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS policies (
            policy_id TEXT PRIMARY KEY,
            max_amount REAL,
            income_condition TEXT
        )
    """
    )

    # ข้อมูล Policies (กฎเกณฑ์)
    # P01: รายได้น้อย (Fixed 6500)
    # P02: ทั่วไป (Max 20000)
    # P03: รายได้สูง (Max 20000)
    cursor.execute(
        "INSERT OR IGNORE INTO policies (policy_id, max_amount, income_condition) VALUES (?, ?, ?)",
        ("P01", 6500, "Income < 6500"),
    )
    cursor.execute(
        "INSERT OR IGNORE INTO policies (policy_id, max_amount, income_condition) VALUES (?, ?, ?)",
        ("P02", 20000, "6500 <= Income <= 50000"),
    )
    cursor.execute(
        "INSERT OR IGNORE INTO policies (policy_id, max_amount, income_condition) VALUES (?, ?, ?)",
        ("P03", 20000, "Income > 50000"),
    )

    # 3. ตาราง Claims (คำขอเยียวยา)
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS claims (
            claim_id TEXT PRIMARY KEY,
            claimant_id INTEGER,
            request_date TEXT,
            status TEXT,
            FOREIGN KEY(claimant_id) REFERENCES claimants(id)
        )
    """
    )

    # 4. ตาราง Compensations (ผลการคำนวณ)
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS compensations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            claim_id TEXT,
            amount REAL,
            calc_date TEXT,
            FOREIGN KEY(claim_id) REFERENCES claims(claim_id)
        )
    """
    )

    # 5. ตาราง Users (สำหรับ Login)
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password TEXT NOT NULL,
            role TEXT NOT NULL
        )
    """
    )

    # ข้อมูล User จำลอง
    cursor.execute("INSERT OR IGNORE INTO users VALUES ('admin', '1234', 'officer')")
    cursor.execute("INSERT OR IGNORE INTO users VALUES ('user', '1234', 'citizen')")

    conn.commit()
    conn.close()
    print("Database setup complete.")


if __name__ == "__main__":
    setup_database()
