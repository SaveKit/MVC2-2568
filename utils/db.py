# utils/db.py
import sqlite3

DB_PATH = "relief_fund.db"


def get_db_connection():
    """ฟังก์ชันกลางสำหรับเชื่อมต่อ Database"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn
