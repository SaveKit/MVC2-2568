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

    conn.commit()
    conn.close()
    print("Database setup complete.")


if __name__ == "__main__":
    setup_database()
