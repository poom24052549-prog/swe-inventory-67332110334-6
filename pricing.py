"""โมดูลคำนวณราคาและส่วนลดของระบบ Inventory (ฉบับ Refactored)

ได้รับการปรับปรุงให้อ่านง่าย มีโครงสร้างชัดเจนตามหลัก Single Responsibility Principle (SRP)
และปฏิบัติตามมาตรฐาน PEP 8 โดยคงพฤติกรรมเดิม (Backward Compatibility) ครบถ้วน 100%
"""

from __future__ import annotations

import datetime
from collections.abc import Sequence

# --- ค่าคงที่ระบบ (Constants) ---
DEFAULT_TAX_RATE: float = 0.07

# เกณฑ์ส่วนลดตามปริมาณการซื้อ (Volume Discounts)
TIER1_QUANTITY_THRESHOLD: int = 50
TIER1_DISCOUNT_MULTIPLIER: float = 0.95  # ลด 5%

TIER2_QUANTITY_THRESHOLD: int = 100
TIER2_DISCOUNT_MULTIPLIER: float = 0.90  # ลด 10%

# สิทธิประโยชน์สมาชิก (Member Benefits)
MEMBER_DISCOUNT_MULTIPLIER: float = 0.95  # ลด 5%
BAHT_PER_MEMBER_POINT: int = 100  # 1 แต้มต่อทุก 100 บาท

# รหัสคูปอง (Coupon Codes)
COUPON_SAVE50_AMOUNT: float = 50.0
COUPON_HALF_MULTIPLIER: float = 0.50
COUPON_NEWYEAR_MULTIPLIER: float = 0.80  # ลด 20% เฉพาะเดือนมกราคม

# สถานะส่วนกลางที่รักษาความเข้ากันได้กับโมดูลเดิม
member_points: dict[str, int] = {}
LOG: list[tuple[str | None, float]] = []


def calculate_item_subtotal(quantity: int, unit_price: float) -> float:
    """คำนวณราคาย่อยของสินค้าแต่ละรายการพร้อมคิดส่วนลดตามปริมาณ"""
    if quantity <= 0:
        return 0.0

    raw_subtotal = quantity * unit_price

    if quantity >= TIER2_QUANTITY_THRESHOLD:
        return raw_subtotal * TIER2_DISCOUNT_MULTIPLIER
    if quantity >= TIER1_QUANTITY_THRESHOLD:
        return raw_subtotal * TIER1_DISCOUNT_MULTIPLIER

    return raw_subtotal


def calculate_items_subtotal(items: Sequence[tuple[str, int, float]]) -> float:
    """คำนวณยอดรวมของสินค้าทั้งหมดก่อนหักส่วนลดสมาชิกและคูปอง"""
    total = 0.0
    for item in items:
        _, quantity, unit_price = item
        total += calculate_item_subtotal(quantity, unit_price)
    return total


def apply_member_benefits(total: float, member: str | None) -> float:
    """คำนวณส่วนลดสมาชิก 5% และสะสมแต้ม 1 แต้มต่อ 100 บาท"""
    if member is None:
        return total

    if member not in member_points:
        member_points[member] = 0

    discounted_total = total * MEMBER_DISCOUNT_MULTIPLIER
    earned_points = int(discounted_total / BAHT_PER_MEMBER_POINT)
    member_points[member] += earned_points

    return discounted_total


def apply_coupon_discount(
    total: float, coupon: str | None, today: datetime.date | None
) -> float:
    """คำนวณส่วนลดตามเงื่อนไขของคูปองแต่ละประเภท"""
    if coupon is None:
        return total

    if coupon == "SAVE50":
        return total - COUPON_SAVE50_AMOUNT

    if coupon == "HALF":
        return total * COUPON_HALF_MULTIPLIER

    if coupon == "NEWYEAR":
        check_date = datetime.date.today() if today is None else today
        if check_date.month == 1:
            return total * COUPON_NEWYEAR_MULTIPLIER

    return total


def apply_tax_and_rounding(total: float, tax_rate: float = DEFAULT_TAX_RATE) -> float:
    """บวกภาษีมูลค่าเพิ่มและปัดเศษทศนิยมเป็น 2 ตำแหน่ง"""
    total_with_tax = total + (total * tax_rate)
    return round(total_with_tax, 2)


def calc(
    items: Sequence[tuple[str, int, float]],
    member: str | None = None,
    coupon: str | None = None,
    today: datetime.date | None = None,
) -> float:
    """ฟังก์ชันหลักสำหรับคำนวณราคาสุทธิของสินค้าพร้อมส่วนลด ภาษี และบันทึก Log

    Parameters:
        items: ลิสต์ของ tuple (ชื่อสินค้า, จำนวน, ราคาต่อหน่วย)
        member: ชื่อสมาชิก (ถ้ามี)
        coupon: รหัสคูปองส่วนลด (ถ้ามี)
        today: วันที่สำหรับตรวจสอบเงื่อนไขคูปอง (ค่าเริ่มต้นคือวันที่ปัจจุบัน)

    Returns:
        float: ราคาสุทธิหลังหักส่วนลดและรวมภาษี (ปัดเศษ 2 ตำแหน่ง)
    """
    # 1. รวมราคาสินค้าพร้อมส่วนลดตามปริมาณ
    total = calculate_items_subtotal(items)

    # 2. คิดส่วนลดสมาชิกและคำนวณแต้มสะสม
    total = apply_member_benefits(total, member)

    # 3. คิดส่วนลดจากคูปอง
    total = apply_coupon_discount(total, coupon, today)

    # 4. หากยอดติดลบ ปรับให้เป็น 0
    if total < 0:
        total = 0.0

    # 5. บวกภาษีและปัดเศษทศนิยม 2 ตำแหน่ง
    final_total = apply_tax_and_rounding(total)

    # 6. บันทึกประวัติการคำนวณลง LOG
    LOG.append((member, final_total))

    return final_total
