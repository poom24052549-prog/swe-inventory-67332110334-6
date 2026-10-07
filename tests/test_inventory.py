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
