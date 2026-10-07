# SWE Inventory Management - Lab 05: TDD, Refactor และ CI/CD

**รายวิชา:** วิศวกรรมซอฟต์แวร์ในยุค AI (Software Engineering in AI Era)  
**ชื่อ-นามสกุล:** นายพชรดนัย มูลสาร (Mr. Pacharadon Moonsara)  
**รหัสนักศึกษา:** 67332110334-6  
**GitHub Username:** [poom24052549-prog](https://github.com/poom24052549-prog)  
**Repository:** [https://github.com/poom24052549-prog/swe-inventory-67332110334-6](https://github.com/poom24052549-prog/swe-inventory-67332110334-6)

---

## 📌 สรุปรายการงานส่ง Lab 05 (Deliverables Checklist - Rubric 100 คะแนน)

งานทุกข้อของ Lab 5 ได้รับการพัฒนา ตรวจสอบ และจัดทำเอกสารตามเกณฑ์ Rubric 100 คะแนนเต็ม:

| # | รายการงานส่ง (Deliverables) | ไฟล์ที่เกี่ยวข้อง | คำอธิบายและผลลัพธ์ |
|:-:|---|---|---|
| 1 | **TDD ของ `low_stock_items`** | [`tests/test_inventory.py`](tests/test_inventory.py)<br>[`inventory.py`](inventory.py) | พัฒนาด้วยกระบวนการ Red-Green-Refactor ครบ 6 กรณีทดสอบ (Threshold ขอบ, เท่ากับพอดี, เรียงตามชื่อ, คลังว่าง, 0, ติดลบ) พร้อมประวัติ Commit แยกชัดเจน |
| 2 | **การจับ Test Gap ของเมธอด `sell`** | [`test-gap.md`](test-gap.md)<br>[`tests/test_inventory.py`](tests/test_inventory.py) | ตารางเปรียบเทียบ 3 คอลัมน์ (กรณีที่ AI ให้มา, กรณีที่ขาด, Test ที่เขียนเสริม) ครอบคลุมค่าขอบ, ค่า 0/ติดลบ, สต็อกไม่พอ, สินค้าไม่มีจริง และความถูกต้องของมูลค่ารวม |
| 3 | **บันทึกการวิเคราะห์ Coverage** | [`coverage-note.md`](coverage-note.md) | ตอบครบ 3 คำถาม: บรรทัดที่หลุดและความเสี่ยง, ทำไม 100% ถึงยังไม่ได้แปลว่า Test ดี (ยกตัวอย่างโค้ดจริง), และการจัดลำดับความสำคัญของ Test 3 ข้อแรก |
| 4 | **วิเคราะห์ Code Smells** | [`smells.md`](smells.md) | วิเคราะห์การทำงานทีละขั้นและระบุ 7 กลิ่นโค้ดใน `pricing_legacy.py` (Global mutable state, Primitive obsession, Magic numbers, God function/SRP, Non-idiomatic comparison ฯลฯ) |
| 5 | **Characterization Test** | [`tests/test_pricing_legacy.py`](tests/test_pricing_legacy.py) | ชุดทดสอบ 20 ข้อ บันทึกพฤติกรรมจริงของโมดูลคิดราคาเดิม ครอบคลุมราคาปกติ, ซื้อจำนวนมาก (เกณฑ์ 49, 50, 99, 100), จำนวน 0, สมาชิกและแต้มสะสม, คูปองทุกแบบ และ State side-effects พร้อม Fixture ล้างค่า |
| 6 | **Refactor โครงสร้างโมดูล Pricing** | [`pricing.py`](pricing.py)<br>[`tests/test_pricing.py`](tests/test_pricing.py) | ปรับปรุงโครงสร้างใหม่ให้อ่านง่าย แยกฟังก์ชันตามหลัก SRP ใช้ค่าคงที่ชัดเจน โดยรักษาความเข้ากันได้ 100% และผ่าน Test ชุดเดิมครบทุกข้อ |
| 7 | **การตั้งค่า Ruff Linter** | [`pyproject.toml`](pyproject.toml) | กำหนด `line-length = 100`, กฎ `E, F, I, UP`, exclude โฟลเดอร์ Lab 4 และ `pricing_legacy.py` รันผ่าน 0 errors |
| 8 | **GitHub Actions CI Workflow** | [`.github/workflows/ci.yml`](.github/workflows/ci.yml) | Pipeline อัตโนมัติ: ดึงโค้ด, ติดตั้ง Python 3.11, ติดตั้ง requirements, ตรวจสอบ Ruff, และรัน Pytest พร้อมเกณฑ์ Coverage ขั้นต่ำ `--cov-fail-under=85` |
| 9 | **ภาพถ่ายยืนยัน CI Checks** | [`screenshots/ci-green.png`](screenshots/ci-green.png)<br>[`screenshots/ci-red.png`](screenshots/ci-red.png) | ภาพหน้าจอการทำงานของ GitHub Actions CI: ภาพผ่านสีเขียว (Green Check) และภาพจงใจล้มเหลวสีแดง (Red Check) จาก Log |
| 10 | **การวิเคราะห์มิติด้านจริยธรรม** | [`ethics.md`](ethics.md) | ตอบ 4 ประเด็นจริยธรรม (ความรับผิดชอบ, ลิขสิทธิ์โค้ด, PDPA ข้อมูลสมาชิก, ความเป็นธรรมของ AI) พร้อมแนวปฏิบัติส่วนบุคคล 150-250 คำ |

---

## 🧪 การทดสอบระบบในเครื่อง (Local Testing)

```bash
# ติดตั้ง dependencies
pip install -r requirements.txt

# ตรวจสอบมาตรฐานโค้ดด้วย Ruff
ruff check .

# รันชุดทดสอบทั้งหมด 53 ข้อ พร้อมวัด Coverage
pytest tests/ --cov=. --cov-report=term-missing --cov-fail-under=85
```
