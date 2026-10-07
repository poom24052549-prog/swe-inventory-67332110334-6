import datetime

import pytest

import pricing_legacy
from pricing_legacy import calc


@pytest.fixture(autouse=True)
def reset_pricing_state():
    """ล้างสถานะ Global Mutable State (member_points และ LOG) ก่อนเริ่มทุก test"""
    pricing_legacy.member_points.clear()
    pricing_legacy.LOG.clear()
    yield
    pricing_legacy.member_points.clear()
    pricing_legacy.LOG.clear()


# --- 1. กลุ่มราคาปกติ (Normal Price) ---

def test_normal_single_item_small_quantity():
    """สินค้าหนึ่งรายการ จำนวนน้อย ไม่ใช้สิทธิ์อะไรเลย"""
    items = [("Notebook", 1, 100.0)]
    total = calc(items)
    assert total == 107.0


def test_normal_multiple_items_small_quantity():
    """สินค้าหลายรายการ จำนวนน้อย ไม่ใช้สิทธิ์อะไรเลย"""
    items = [("Pen", 2, 20.0), ("Ruler", 1, 10.0)]
    # (2*20 + 1*10) = 50 * 1.07 = 53.5
    total = calc(items)
    assert total == 53.5


# --- 2. กลุ่มซื้อจำนวนมาก (Bulk / Volume Discount) ---

def test_bulk_discount_below_first_tier_49():
    """ซื้อ 49 ชิ้น (ต่ำกว่าเกณฑ์ 50 ชิ้น ไม่ได้รับส่วนลด)"""
    items = [("ItemA", 49, 10.0)]
    # 490 * 1.07 = 524.3
    total = calc(items)
    assert total == 524.3


def test_bulk_discount_exact_first_tier_50():
    """ซื้อ 50 ชิ้น พอดีเกณฑ์ขั้นที่หนึ่ง (ลด 5%)"""
    items = [("ItemA", 50, 10.0)]
    # 500 * 0.95 = 475; 475 * 1.07 = 508.25
    total = calc(items)
    assert total == 508.25


def test_bulk_discount_below_second_tier_99():
    """ซื้อ 99 ชิ้น (อยู่ในเกณฑ์ลด 5%)"""
    items = [("ItemA", 99, 10.0)]
    # 990 * 0.95 = 940.5; 940.5 * 1.07 = 1006.335 -> 1006.34
    total = calc(items)
    assert total == 1006.34


def test_bulk_discount_exact_second_tier_100():
    """ซื้อ 100 ชิ้น พอดีเกณฑ์ขั้นที่สอง (ลด 10%)"""
    items = [("ItemA", 100, 10.0)]
    # 1000 * 0.9 = 900; 900 * 1.07 = 963.0
    total = calc(items)
    assert total == 963.0


# --- 3. กลุ่มจำนวนเป็นศูนย์หรือติดลบ (Zero and Negative Quantity) ---

def test_zero_quantity_single_item():
    """สินค้าที่ใส่จำนวน 0 มา คืนยอด 0.0"""
    items = [("Pencil", 0, 50.0)]
    total = calc(items)
    assert total == 0.0


def test_negative_quantity_single_item():
    """สินค้าที่ใส่จำนวนติดลบ คืนยอด 0.0"""
    items = [("Pencil", -5, 50.0)]
    total = calc(items)
    assert total == 0.0


def test_mixed_zero_and_valid_quantity():
    """สินค้าผสมระหว่างจำนวน 0 และจำนวนปกติ ข้ามตัวที่เป็น 0"""
    items = [("ZeroItem", 0, 100.0), ("ValidItem", 1, 100.0)]
    total = calc(items)
    assert total == 107.0


# --- 4. กลุ่มสมาชิก (Member Discount & Loyalty Points) ---

def test_member_discount_and_points_awarded():
    """สมาชิกลด 5% และสะสมแต้ม (1 แต้มต่อ 100 บาท)"""
    items = [("Book", 1, 1000.0)]
    # 1000 * 0.95 = 950; points = int(950 / 100) = 9; tax = 950 * 1.07 = 1016.5
    total = calc(items, member="Poom")
    assert total == 1016.5
    assert pricing_legacy.member_points["Poom"] == 9


def test_member_discount_below_point_threshold():
    """สมาชิกซื้อยอดน้อยกว่า 100 บาทหลังส่วนลด ได้ 0 แต้ม"""
    items = [("Pen", 1, 100.0)]
    # 100 * 0.95 = 95; points = int(95 / 100) = 0; tax = 95 * 1.07 = 101.65
    total = calc(items, member="Poom")
    assert total == 101.65
    assert pricing_legacy.member_points["Poom"] == 0


def test_member_accumulates_points_over_calls():
    """แต้มของสมาชิกสะสมเพิ่มขึ้นจากการซื้อหลายครั้ง"""
    calc([("Pen", 1, 100.0)], member="Alice")  # 95 บาท -> +0 แต้ม
    calc([("Book", 1, 200.0)], member="Alice")  # 190 บาท -> +1 แต้ม
    assert pricing_legacy.member_points["Alice"] == 1


# --- 5. กลุ่มคูปอง (Coupons) ---

def test_coupon_save50():
    """คูปอง SAVE50 หักลด 50 บาท"""
    items = [("Bag", 1, 100.0)]
    # 100 - 50 = 50; 50 * 1.07 = 53.5
    total = calc(items, coupon="SAVE50")
    assert total == 53.5


def test_coupon_half():
    """คูปอง HALF ลด 50%"""
    items = [("Bag", 1, 100.0)]
    # 100 * 0.5 = 50; 50 * 1.07 = 53.5
    total = calc(items, coupon="HALF")
    assert total == 53.5


def test_coupon_newyear_in_january():
    """คูปอง NEWYEAR ใช้ในเดือนมกราคม ลด 20%"""
    items = [("Bag", 1, 100.0)]
    jan_date = datetime.date(2026, 1, 15)
    # 100 * 0.8 = 80; 80 * 1.07 = 85.6
    total = calc(items, coupon="NEWYEAR", today=jan_date)
    assert total == 85.6


def test_coupon_newyear_outside_january():
    """คูปอง NEWYEAR ใช้นอกเดือนมกราคม ไม่ได้รับส่วนลด"""
    items = [("Bag", 1, 100.0)]
    may_date = datetime.date(2026, 5, 20)
    # 100 (ไม่ลด) * 1.07 = 107.0
    total = calc(items, coupon="NEWYEAR", today=may_date)
    assert total == 107.0


def test_unknown_coupon_ignored():
    """คูปองที่ไม่รู้จัก ไม่ส่งผลต่อราคา"""
    items = [("Bag", 1, 100.0)]
    total = calc(items, coupon="INVALID")
    assert total == 107.0


# --- 6. กลุ่มยอดติดลบ (Negative / Floor at Zero) ---

def test_discount_exceeds_total_floored_at_zero():
    """ส่วนลดคูปองมากกว่าราคาสินค้า ยอดต้องถูกปัดเป็น 0.0 ไม่ติดลบ"""
    items = [("Candy", 1, 30.0)]
    # 30 - 50 = -20 -> floor at 0 -> 0 * 1.07 = 0.0
    total = calc(items, coupon="SAVE50")
    assert total == 0.0


# --- 7. กลุ่มค่าที่ฟังก์ชันเก็บไว้ (Logged Side Effects) ---

def test_logging_side_effect_anonymous_customer():
    """ตรวจสอบการบันทึกประวัติลง LOG เมื่อไม่ระบุสมาชิก"""
    items = [("Notebook", 1, 100.0)]
    total = calc(items)
    assert pricing_legacy.LOG == [(None, total)]


def test_logging_side_effect_member_customer():
    """ตรวจสอบการบันทึกประวัติลง LOG เมื่อระบุชื่อสมาชิก"""
    items = [("Notebook", 1, 100.0)]
    total = calc(items, member="Bob")
    assert pricing_legacy.LOG == [("Bob", total)]
