# models/claim_models.py
from datetime import datetime


class ClaimModel:
    """Base Class สำหรับคำขอทั่วไป"""

    def __init__(self, income):
        self.income = income

    def calculate_compensation(self):
        """Logic คำนวณสำหรับคนทั่วไป (General)
        รายได้ 6500 - 50000 ได้ตามรายได้จริง แต่ไม่เกิน 20,000"""
        return min(self.income, 20000)


class LowIncomeClaimModel(ClaimModel):
    """Class สำหรับผู้มีรายได้น้อย (< 6500)"""

    def calculate_compensation(self):
        """รายได้น้อยกว่า 6500 ได้รับทันที 6500"""
        return 6500


class HighIncomeClaimModel(ClaimModel):
    """Class สำหรับผู้มีรายได้สูง (> 50000)"""

    def calculate_compensation(self):
        """รายได้เกิน 50000 ได้รายได้หาร 5 แต่ไม่เกิน 20,000"""
        calculated = self.income / 5
        return min(calculated, 20000)


# Factory Method เพื่อสร้าง ClaimModel ที่เหมาะสมตามรายได้
def get_claim_model(income):
    if income < 6500:
        return LowIncomeClaimModel(income)
    elif income > 50000:
        return HighIncomeClaimModel(income)
    else:
        return ClaimModel(income)
