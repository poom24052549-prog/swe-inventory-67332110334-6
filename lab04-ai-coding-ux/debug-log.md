# Debug Log: discount.py (Evidence-Based Debugging)

เอกสารบันทึกกระบวนการ Debugging แบบมีหลักฐาน (Evidence-Based Debugging) เพื่อค้นหาและแก้ไข Root Cause ของข้อผิดพลาดในโมดูล `discount.py` ตามระเบียบวิธี 5 ขั้นตอน

---

## 1. ผลการรัน Test ครั้งแรก (Reproduce Step)

คำสั่งที่ใช้รัน:
```bash
python -m pytest tests/test_discount.py -v
```

ผลลัพธ์ Traceback ที่ได้จากการรันจริง:
```text
============================= test session starts =============================
platform win32 -- Python 3.12.10, pytest-9.1.1, pluggy-1.6.0
rootdir: C:\Users\poom\.gemini\antigravity\scratch\swe-inventory\lab04-ai-coding-ux
collected 6 items

tests/test_discount.py::test_apply_discount_basic FAILED                 [ 16%]
tests/test_discount.py::test_apply_discount_zero PASSED                  [ 33%]
tests/test_discount.py::test_bulk_total FAILED                           [ 50%]
tests/test_discount.py::test_average_price PASSED                        [ 66%]
tests/test_discount.py::test_average_price_empty FAILED                  [ 83%]
tests/test_discount.py::test_cheapest_n FAILED                           [100%]

================================== FAILURES ===================================
__________________________ test_apply_discount_basic __________________________
    def test_apply_discount_basic():
        # ลด 10% จาก 100 บาท ควรเหลือ 90 บาท
>       assert apply_discount(100.0, 10) == 90.0
E       assert 99.9 == 90.0
E        +  where 99.9 = apply_discount(100.0, 10)
tests\test_discount.py:8: AssertionError

_______________________________ test_bulk_total _______________________________
    def test_bulk_total():
        # (100 + 100 + 100) = 300 ลด 10% ควรเหลือ 270
>       assert bulk_total([100.0, 100.0, 100.0], 10) == 270.0
E       assert 299.9 == 270.0
E        +  where 299.9 = bulk_total([100.0, 100.0, 100.0], 10)
tests\test_discount.py:18: AssertionError

__________________________ test_average_price_empty ___________________________
    def test_average_price_empty():
        # คลังว่างควรได้ 0.0 ไม่ใช่ crash
>       assert average_price([]) == 0.0
discount.py:18: in average_price
>       return sum(prices) / len(prices)
E       ZeroDivisionError: division by zero
tests\test_discount.py:28: ZeroDivisionError

_______________________________ test_cheapest_n _______________________________
    def test_cheapest_n():
        # ถูกสุด 2 รายการของ [50, 10, 30, 20] = [10, 20]
>       assert cheapest_n([50.0, 10.0, 30.0, 20.0], 2) == [10.0, 20.0]
E       assert [20.0] == [10.0, 20.0]
E         At index 0 diff: 20.0 != 10.0
E         Right contains one more item: 20.0
tests\test_discount.py:33: AssertionError
=========================== short test summary info ===========================
FAILED tests/test_discount.py::test_apply_discount_basic - assert 99.9 == 90.0
FAILED tests/test_discount.py::test_bulk_total - assert 299.9 == 270.0
FAILED tests/test_discount.py::test_average_price_empty - ZeroDivisionError: division by zero
FAILED tests/test_discount.py::test_cheapest_n - assert [20.0] == [10.0, 20.0]
========================= 4 failed, 2 passed in 0.10s =========================
```

---

## 2. ตารางไล่ Root Cause ทีละข้อตามระเบียบวิธี 5 ขั้นตอน (Phase 3A)

| test ที่ไม่ผ่าน | traceback หรือ assertion ที่เห็น | สมมติฐาน root cause | วิธียืนยัน | การแก้ |
| :--- | :--- | :--- | :--- | :--- |
| **test_apply_discount_basic** | `assert 99.9 == 90.0`<br>(ใน `apply_discount(100.0, 10)`) | สูตรคำนวณส่วนลดผิด โดยนำค่า `percent / 100` ไปลบออกจาก `price` โดยตรง แทนที่จะนำมูลค่าส่วนลด `price * (percent / 100)` ไปหักออก ทำให้ 100 - 0.1 = 99.9 | ทดลองคำนวณใน Python CLI:<br>`100.0 - 10/100` -> `99.9`<br>`100.0 * (1 - 10/100)` -> `90.0` พบว่าสูตรหลังให้ค่าถูกต้อง | แก้ไขบรรทัดที่ 5 เป็น:<br>`return price * (1 - percent / 100)` |
| **test_bulk_total** | `assert 299.9 == 270.0`<br>(ใน `bulk_total([100, 100, 100], 10)`) | ฟังก์ชัน `bulk_total` รวมยอดได้ถูกต้อง (`total = 300.0`) แต่ผลลัพธ์ล้มเหลวเพราะเรียกใช้ `apply_discount` ซึ่งมี root cause จากบั๊กข้อแรก (`300.0 - 0.1 = 299.9`) | ตรวจสอบการทำงานของ `bulk_total`: เมื่อผลรวมคือ 300 และส่งเข้า `apply_discount` ที่แก้แล้ว จะได้ `300 * 0.9 = 270.0` ทันที | แก้ที่ Root Cause ในฟังก์ชัน `apply_discount` โดยไม่ต้องแก้โค้ดใน `bulk_total` |
| **test_average_price_empty** | `ZeroDivisionError: division by zero`<br>ที่ `sum(prices) / len(prices)` | ฟังก์ชันไม่ได้ตรวจสอบกรณีขอบเขต (Edge Case) เมื่อรับค่าเป็น List ว่าง (`[]`) ทำให้ `len([])` มีค่าเป็น 0 แล้วเกิดการหารด้วยศูนย์ทันที | รัน `len([])` ใน Python ได้ 0 และ `0 / 0` ให้ `ZeroDivisionError` ตรงกับ Traceback | เพิ่มเงื่อนไขตรวจสอบ Guard Clause ก่อนการหาร:<br>`if not prices:`<br>`    return 0.0` |
| **test_cheapest_n** | `assert [20.0] == [10.0, 20.0]`<br>(ได้สมาชิกตัวเดียวและข้ามตัวแรก) | การตัดช่วงข้อมูลผิดขอบเขต (Slicing Error / Off-by-one): โค้ดเขียน `ordered[1:n]` ทำให้เริ่มตัดที่ index 1 จึงข้ามสมาชิกตัวแรกสุดที่ราคาถูกที่สุด (`10.0`) ไป และได้จำนวนสมาชิกน้อยกว่า n ตัว | ทดสอบ Slice ใน Python:<br>`s = [10.0, 20.0, 30.0, 50.0]`<br>`s[1:2]` ได้ `[20.0]`<br>`s[:2]` ได้ `[10.0, 20.0]` | แก้ไขบรรทัดที่ 26 เป็น:<br>`return ordered[:n]` |

---

## 3. กับดักที่ตั้งใจวางไว้ (Edge Case Trap Analysis)

ในชุดการทดสอบนี้ มี 2 Test Case ที่ **ผ่าน (PASSED)** ตั้งแต่แรกทั้งที่โค้ดยังมีข้อบกพร่องแฝงอยู่ ได้แก่:
1. `test_apply_discount_zero`:
   - ทดสอบลด 0% จากราคา 250.0 บาท
   - เมื่อคำนวณตามสูตรเดิมที่มีบั๊ก: `250.0 - (0 / 100) = 250.0` ซึ่งบังเอิญได้ผลลัพธ์ตรงกับที่คาดหวังพอดิบพอดี ทำให้การทดสอบผ่านไปได้อย่างหลอกตา หากมีเพียง Test นี้ข้อเดียว ผู้พัฒนาจะหลงคิดว่าฟังก์ชันคำนวณส่วนลดทำงานได้ถูกต้องสมบูรณ์
2. `test_average_price`:
   - ทดสอบหาค่าเฉลี่ยของ `[10.0, 20.0, 30.0]` ซึ่งเป็นกรณีปกติ (Happy Path ที่มีข้อมูล 3 ชิ้น) ตัวหาร `len(prices) = 3` จึงทำงานได้ปกติและได้ค่าเฉลี่ย 20.0 แต่ไม่ได้ครอบคลุม Edge Case กรณีลิสต์ว่าง

**บทเรียนสำคัญ:** การที่ Unit Test ผ่านทุกข้อ ไม่ได้เป็นเครื่องการันตีว่าโปรแกรมปราศจากบั๊ก 100% หากชุดการทดสอบขาด Test Coverage ในส่วนของ Edge Cases และ Boundary Conditions

---

## 4. ผลการทดสอบหลังการแก้ไขทั้งหมด (Re-run Verification)

คำสั่งที่ใช้ทดสอบ:
```bash
python -m pytest tests/test_discount.py -v
```

ผลลัพธ์หลังแก้ไข:
```text
============================= test session starts =============================
platform win32 -- Python 3.12.10, pytest-9.1.1, pluggy-1.6.0
rootdir: C:\Users\poom\.gemini\antigravity\scratch\swe-inventory\lab04-ai-coding-ux
collected 6 items

tests/test_discount.py::test_apply_discount_basic PASSED                 [ 16%]
tests/test_discount.py::test_apply_discount_zero PASSED                  [ 33%]
tests/test_discount.py::test_bulk_total PASSED                           [ 50%]
tests/test_discount.py::test_average_price PASSED                        [ 66%]
tests/test_discount.py::test_average_price_empty PASSED                  [ 83%]
tests/test_discount.py::test_cheapest_n PASSED                           [100%]

============================== 6 passed in 0.03s ==============================
```
**สรุปผล:** ทุก Test Case ผ่านการทดสอบทั้งหมด (6 passed, 0 failed) 100%
