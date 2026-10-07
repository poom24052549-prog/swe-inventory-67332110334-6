import datetime

import pytest

import pricing
from pricing import calc


@pytest.fixture(autouse=True)
def reset_pricing_state():
    """ล้างสถานะ Global State (member_points และ LOG)
    ของโมดูล pricing ที่ผ่านการ refactor ก่อนเริ่มทุก test
    """
    pricing.member_points.clear()
    pricing.LOG.clear()
    yield
    pricing.member_points.clear()
    pricing.LOG.clear()


# --- 1. กลุ่มราคาปกติ (Normal Price) ---

def test_normal_single_item_small_quantity():
    """สินค้าหนึ่งรายการ จำนวนน้อย ไม่ใช้สิทธิ์อะไรเลย"""
    items = [("Notebook", 1, 100.0)]
    total = calc(items)
    assert total == 107.0


def test_normal_multiple_items_small_quantity():
    """สินค้าหลายรายการ จำนวนน้อย ไม่ใช้สิทธิ์อะไรเลย"""
    items = [("Pen", 2, 20.0), ("Ruler", 1, 10.0)]
    total = calc(items)
    assert total == 53.5


# --- 2. กลุ่มซื้อจำนวนมาก (Bulk / Volume Discount) ---

def test_bulk_discount_below_first_tier_49():
    """ซื้อ 49 ชิ้น (ต่ำกว่าเกณฑ์ 50 ชิ้น ไม่ได้รับส่วนลด)"""
    items = [("ItemA", 49, 10.0)]
    total = calc(items)
    assert total == 524.3


def test_bulk_discount_exact_first_tier_50():
    """ซื้อ 50 ชิ้น พอดีเกณฑ์ขั้นที่หนึ่ง (ลด 5%)"""
    items = [("ItemA", 50, 10.0)]
    total = calc(items)
    assert total == 508.25


def test_bulk_discount_below_second_tier_99():
    """ซื้อ 99 ชิ้น (อยู่ในเกณฑ์ลด 5%)"""
    items = [("ItemA", 99, 10.0)]
    total = calc(items)
    assert total == 1006.34


def test_bulk_discount_exact_second_tier_100():
    """ซื้อ 100 ชิ้น พอดีเกณฑ์ขั้นที่สอง (ลด 10%)"""
    items = [("ItemA", 100, 10.0)]
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
    total = calc(items, member="Poom")
    assert total == 1016.5
    assert pricing.member_points["Poom"] == 9


def test_member_discount_below_point_threshold():
    """สมาชิกซื้อยอดน้อยกว่า 100 บาทหลังส่วนลด ได้ 0 แต้ม"""
    items = [("Pen", 1, 100.0)]
    total = calc(items, member="Poom")
    assert total == 101.65
    assert pricing.member_points["Poom"] == 0


def test_member_accumulates_points_over_calls():
    """แต้มของสมาชิกสะสมเพิ่มขึ้นจากการซื้อหลายครั้ง"""
    calc([("Pen", 1, 100.0)], member="Alice")
    calc([("Book", 1, 200.0)], member="Alice")
    assert pricing.member_points["Alice"] == 1


# --- 5. กลุ่มคูปอง (Coupons) ---

def test_coupon_save50():
    """คูปอง SAVE50 หักลด 50 บาท"""
    items = [("Bag", 1, 100.0)]
    total = calc(items, coupon="SAVE50")
    assert total == 53.5


def test_coupon_half():
    """คูปอง HALF ลด 50%"""
    items = [("Bag", 1, 100.0)]
    total = calc(items, coupon="HALF")
    assert total == 53.5


def test_coupon_newyear_in_january():
    """คูปอง NEWYEAR ใช้ในเดือนมกราคม ลด 20%"""
    items = [("Bag", 1, 100.0)]
    jan_date = datetime.date(2026, 1, 15)
    total = calc(items, coupon="NEWYEAR", today=jan_date)
    assert total == 85.6


def test_coupon_newyear_outside_january():
    """คูปอง NEWYEAR ใช้นอกเดือนมกราคม ไม่ได้รับส่วนลด"""
    items = [("Bag", 1, 100.0)]
    may_date = datetime.date(2026, 5, 20)
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
    total = calc(items, coupon="SAVE50")
    assert total == 0.0


# --- 7. กลุ่มค่าที่ฟังก์ชันเก็บไว้ (Logged Side Effects) ---

def test_logging_side_effect_anonymous_customer():
    """ตรวจสอบการบันทึกประวัติลง LOG เมื่อไม่ระบุสมาชิก"""
    items = [("Notebook", 1, 100.0)]
    total = calc(items)
    assert pricing.LOG == [(None, total)]


def test_logging_side_effect_member_customer():
    """ตรวจสอบการบันทึกประวัติลง LOG เมื่อระบุชื่อสมาชิก"""
    items = [("Notebook", 1, 100.0)]
    total = calc(items, member="Bob")
    assert pricing.LOG == [("Bob", total)]
