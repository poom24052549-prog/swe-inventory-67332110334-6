import pytest

from inventory import Inventory

# --- ขั้นที่ 2: TDD สำหรับ low_stock_items (6 กรณี) ---

def test_low_stock_items_all_above_threshold():
    # กรณี 1: สินค้าทุกรายการมีจำนวนมากกว่า threshold -> คืน list ว่าง
    inv = Inventory()
    inv.add_item("Apple", 15, 10.0)
    inv.add_item("Banana", 20, 5.0)
    assert inv.low_stock_items(10) == []


def test_low_stock_items_exact_threshold():
    # กรณี 2: มีสินค้าที่จำนวนเท่ากับ threshold พอดี -> ต้องถูกนับรวมด้วย
    inv = Inventory()
    inv.add_item("Apple", 10, 10.0)
    inv.add_item("Banana", 25, 5.0)
    assert inv.low_stock_items(10) == ["Apple"]


def test_low_stock_items_sorted_by_name():
    # กรณี 3: มีสินค้าเข้าเกณฑ์หลายรายการ -> ผลลัพธ์เรียงตามชื่อ ไม่ใช่ตามลำดับที่เพิ่ม
    inv = Inventory()
    inv.add_item("Orange", 3, 15.0)
    inv.add_item("Apple", 5, 10.0)
    inv.add_item("Banana", 2, 5.0)
    inv.add_item("Watermelon", 50, 30.0)
    assert inv.low_stock_items(5) == ["Apple", "Banana", "Orange"]


def test_low_stock_items_empty_inventory():
    # กรณี 4: คลังว่าง -> คืน list ว่าง ไม่ใช่ error
    inv = Inventory()
    assert inv.low_stock_items(10) == []


def test_low_stock_items_zero_threshold():
    # กรณี 5: threshold เป็น 0 -> คืนเฉพาะสินค้าที่เหลือ 0
    inv = Inventory()
    inv.add_item("OutStock", 0, 100.0)
    inv.add_item("InStock", 1, 50.0)
    assert inv.low_stock_items(0) == ["OutStock"]


def test_low_stock_items_negative_threshold():
    # กรณี 6: threshold ติดลบ -> คืน list ว่าง เนื่องจากจำนวนสินค้าไม่ติดลบ
    inv = Inventory()
    inv.add_item("Apple", 5, 10.0)
    assert inv.low_stock_items(-1) == []


# --- ขั้นที่ 4: Unit tests สำหรับ sell (AI baseline vs Edge cases ที่เขียนเสริม) ---

def test_sell_normal_ai_baseline():
    """กรณีปกติที่ AI มักจะเขียนให้ (Happy path): ขายสินค้าจำนวนปกติ"""
    inv = Inventory()
    inv.add_item("Book", 10, 100.0)
    remaining = inv.sell("Book", 3)
    assert remaining == 7
    assert inv._items["Book"].quantity == 7


def test_sell_exact_boundary():
    """เขียนเสริม 1 (ค่าขอบ): ขายเท่ากับจำนวนที่เหลือทั้งหมดพอดี ต้องเหลือ 0"""
    inv = Inventory()
    inv.add_item("Book", 10, 100.0)
    remaining = inv.sell("Book", 10)
    assert remaining == 0
    assert inv._items["Book"].quantity == 0


def test_sell_zero_amount():
    """เขียนเสริม 2 (ค่าที่ไม่ควรรับ): ขายจำนวน 0 ต้อง raise ValueError"""
    inv = Inventory()
    inv.add_item("Book", 10, 100.0)
    with pytest.raises(ValueError) as excinfo:
        inv.sell("Book", 0)
    assert "จำนวนที่ขายต้องมากกว่าศูนย์" in str(excinfo.value)


def test_sell_negative_amount():
    """เขียนเสริม 3 (ค่าที่ไม่ควรรับ): ขายจำนวนติดลบ ต้อง raise ValueError"""
    inv = Inventory()
    inv.add_item("Book", 10, 100.0)
    with pytest.raises(ValueError) as excinfo:
        inv.sell("Book", -5)
    assert "จำนวนที่ขายต้องมากกว่าศูนย์" in str(excinfo.value)


def test_sell_exceeds_quantity():
    """เขียนเสริม 4 (ค่าที่ไม่ควรรับ): ขายเกินจำนวนคงเหลือ ต้อง raise ValueError พร้อมข้อความเตือน"""
    inv = Inventory()
    inv.add_item("Book", 10, 100.0)
    with pytest.raises(ValueError) as excinfo:
        inv.sell("Book", 11)
    assert "ไม่เพียงพอสำหรับการขาย 11 ชิ้น" in str(excinfo.value)
    assert inv._items["Book"].quantity == 10


def test_sell_nonexistent_item():
    """เขียนเสริม 5 (เส้นทาง error): ขายสินค้าที่ไม่มีในคลัง ต้อง raise KeyError"""
    inv = Inventory()
    inv.add_item("Book", 10, 100.0)
    with pytest.raises(KeyError) as excinfo:
        inv.sell("Pen", 1)
    assert "ไม่พบสินค้า 'Pen' ในระบบ" in str(excinfo.value)


def test_sell_impact_on_total_value():
    """เขียนเสริม 6 (ความถูกต้องของระบบ): ตรวจสอบว่ายอดมูลค่ารวม get_total_value ลดลงถูกต้องตามการขาย"""
    inv = Inventory()
    inv.add_item("Book", 10, 100.0)
    inv.add_item("Pen", 5, 20.0)
    assert inv.get_total_value() == 1100.0
    inv.sell("Book", 4)
    assert inv.get_total_value() == 700.0
