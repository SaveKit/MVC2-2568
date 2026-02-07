# models/claim_models.py
from dataclasses import dataclass


class ClaimModel:
    """Base Class สำหรับคำขอทั่วไป"""

    def __init__(self, income, policy_limit):
        self.income = income
        self.policy_limit = policy_limit

    def calculate_compensation(self):
        """Logic คำนวณสำหรับคนทั่วไป (General)
        รายได้ 6500 - 50000 ได้ตามรายได้จริง แต่ไม่เกิน 20,000"""
        return min(self.income, self.policy_limit)


class LowIncomeClaimModel(ClaimModel):
    """Class สำหรับผู้มีรายได้น้อย"""

    def calculate_compensation(self):
        # กรณีรายได้น้อย จ่ายตามยอดที่กำหนดใน policy_limit (6500)
        return self.policy_limit


class HighIncomeClaimModel(ClaimModel):
    """Class สำหรับผู้มีรายได้สูง"""

    def calculate_compensation(self):
        """รายได้เกิน 50000 ได้รายได้หาร 5 แต่ไม่เกิน 20,000"""
        calculated = self.income / 5
        return min(calculated, self.policy_limit)


# Factory Method เพื่อสร้าง ClaimModel ที่เหมาะสมตามรายได้
def get_claim_model(income, policy_limit):
    if income < 6500:
        return LowIncomeClaimModel(income, policy_limit)
    elif income > 50000:
        return HighIncomeClaimModel(income, policy_limit)
    else:
        return ClaimModel(income, policy_limit)
