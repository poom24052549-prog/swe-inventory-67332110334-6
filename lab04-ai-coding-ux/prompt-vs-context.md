# การเปรียบเทียบ Prompt Engineering กับ Context Engineering

เอกสารบันทึกการทดลองสั่งงาน AI Coding Assistant ในโจทย์เดียวกันจำนวน 2 รอบ เพื่อเปรียบเทียบความแตกต่างระหว่างการสั่งงานแบบไม่มีบริบท (Prompt Engineering ขั้นพื้นฐาน) กับการส่งเสริมบริบทที่ครบถ้วน (Context Engineering)

---

## 1. นิยามและความแตกต่างเชิงแนวคิด

- **Prompt Engineering:** การออกแบบข้อความคำสั่งให้มีความชัดเจน เจาะจง ระบุสิ่งที่ต้องการ เช่น ชนิดของฟังก์ชัน พารามิเตอร์ ผลลัพธ์ที่ต้องการ หรือคำอธิบายบทบาท
- **Context Engineering:** การจัดเตรียมและป้อนข้อมูลแวดล้อม (Context) ที่จำเป็นให้ครบถ้วนก่อนส่งให้โมเดลประมวลผล เช่น โค้ดต้นฉบับทั้งไฟล์ โครงสร้างข้อมูล (Data Structure) เดิม, ข้อกำหนดด้านความปลอดภัย/สถาปัตยกรรม (เช่น Thread-safety, Atomicity), Coding Conventions, รวมถึงชุด Unit Test ที่ผลลัพธ์ต้องผ่าน

### ตารางเปรียบเทียบความแตกต่าง

| มิติการพิจารณา | Prompt ที่บกพร่อง (ขาด Context) | Prompt ที่มี Context ครบถ้วน |
| :--- | :--- | :--- |
| **ความชัดของงาน** | สั่งคลุมเครือ เช่น *"เขียน function ลด stock"* ไม่ระบุประเภทข้อมูลและพฤติกรรม | ระบุ Function Signature, ชนิดของ Exception ที่ต้อง Raise, และรูปแบบค่าที่ Return |
| **ความเข้ากันกับโค้ดเดิม** | ไม่แนบโค้ดเดิมเลย ทำให้ AI เดาโครงสร้างข้อมูลขึ้นมาเอง | แนบคลาส `Inventory` และ `InventoryItem` เดิม ให้ AI อิง Interface และ State เดิม |
| **การตรวจสอบ (Verification)** | ไม่บอกเกณฑ์การตรวจสอบหรือเคสทดสอบที่ต้องการ | แนบเงื่อนไขและ Unit Test Cases ที่ Output ต้องผ่านทุกข้อ (รวมถึง Edge Cases) |
| **ข้อจำกัด (Constraints)** | ไม่ระบุข้อจำกัดของระบบ | ระบุชัดเจนว่าห้ามใช้ Library ภายนอก และต้องเป็น Atomic Operation (Rollback หากไม่สำเร็จ) |

---

## 2. การทดลองสั่งงานรอบที่ 1: Prompt สั้น ขาด Context

### คำสั่ง Prompt (รอบที่ 1):
```text
เขียน function sell_many ใน Python สำหรับลด stock สินค้าหลายรายการพร้อมกัน
```

### ผลลัพธ์โค้ดที่ AI สร้างขึ้น (รอบที่ 1):
```python
def sell_many(inventory, items_to_sell):
    """
    ลด stock สินค้าหลายรายการ
    items_to_sell: dict ของ {item_name: quantity}
    """
    for item, qty in items_to_sell.items():
        if item in inventory:
            if inventory[item] >= qty:
                inventory[item] -= qty
            else:
                return f"Error: สินค้า {item} มีไม่พอ"
        else:
            return f"Error: ไม่พบสินค้า {item}"
    return "ขายสำเร็จทั้งหมด"
```

### การประเมินผลลัพธ์รอบที่ 1:
1. **เข้ากับโค้ดเดิมไม่ได้ (Interface Mismatch):** AI สันนิษฐานว่า `inventory` คือ `dict[str, int]` ธรรมดา ไม่ได้เรียกใช้คลาส `Inventory` หรือออบเจกต์ `InventoryItem` ที่มีอยู่ในระบบจริง
2. **ละเมิดหลัก Atomicity อย่างร้ายแรง:** มีการหักยอดสินค้าชิ้นแรก ๆ ไปแล้วใน `inventory[item] -= qty` ก่อนที่ลูปจะพบว่าสินค้าชิ้นถัดไปสต็อกไม่พอ ทำให้ข้อมูลสินค้าชิ้นแรกถูกหักไปฟรี ๆ โดยไม่มีการย้อนคืน (Rollback)
3. **การจัดการ Exception ผิดหลักวิศวกรรม:** ส่งคืนข้อความเป็น `str` แทนที่จะ Raise Exception ตามมาตรฐานของระบบเดิม (`KeyError`, `ValueError`)
4. **ไม่มีการตรวจสอบความถูกต้อง:** ไม่เช็คจำนวนติดลบหรือสต็อกที่เป็นศูนย์

---

## 3. การทดลองสั่งงานรอบที่ 2: Prompt ที่มี Context ครบถ้วน

### คำสั่ง Prompt (รอบที่ 2):
```text
ปรับปรุงเมธอด sell() ของคลาส Inventory ด้านล่างให้รองรับการขายหลายรายการพร้อมกัน

[โค้ด inventory.py ฉบับสมบูรณ์]:
class InventoryItem:
    def __init__(self, name: str, quantity: int, price: float):
        if not name or not name.strip():
            raise ValueError("ชื่อสินค้าต้องไม่ว่างเปล่า")
        if quantity < 0:
            raise ValueError("จำนวนสินค้าต้องไม่ติดลบ")
        if price <= 0:
            raise ValueError("ราคาต้องมากกว่าศูนย์")
        self.name = name.strip()
        self.quantity = quantity
        self.price = price

class Inventory:
    def __init__(self):
        self._items: dict[str, InventoryItem] = {}

    def add_item(self, name: str, quantity: int, price: float) -> InventoryItem:
        if name in self._items:
            raise ValueError(f"สินค้า '{name}' มีอยู่ในระบบแล้ว")
        item = InventoryItem(name, quantity, price)
        self._items[name] = item
        return item

    def restock(self, name: str, amount: int) -> int:
        if name not in self._items:
            raise KeyError(f"ไม่พบสินค้า '{name}' ในระบบ")
        if amount <= 0:
            raise ValueError("จำนวนที่เติมต้องมากกว่าศูนย์")
        self._items[name].quantity += amount
        return self._items[name].quantity

    def sell(self, name: str, amount: int) -> int:
        if name not in self._items:
            raise KeyError(f"ไม่พบสินค้า '{name}' ในระบบ")
        if amount <= 0:
            raise ValueError("จำนวนที่ขายต้องมากกว่าศูนย์")
        if self._items[name].quantity < amount:
            raise ValueError(
                f"สินค้า '{name}' คงเหลือ {self._items[name].quantity} ชิ้น ไม่เพียงพอสำหรับการขาย {amount} ชิ้น"
            )
        self._items[name].quantity -= amount
        return self._items[name].quantity

    def get_total_value(self) -> float:
        return sum(item.quantity * item.price for item in self._items.values())

ข้อกำหนด (Requirements):
- เพิ่มเมธอด sell_many(orders: dict[str, int]) -> dict[str, int] คืน {ชื่อสินค้า: คงเหลือ}
- ถ้ามีรายการใดรายการหนึ่ง stock ไม่พอ ต้อง raise ValueError และต้องไม่หักรายการใดเลย ทุกรายการต้องสำเร็จพร้อมกันหรือไม่สำเร็จเลย (Atomic Transaction)
- ใช้ exception แบบเดียวกับเมธอดเดิม (KeyError เมื่อไม่พบสินค้า, ValueError เมื่อจำนวนผิดหรือของไม่พอ)
- ห้ามใช้ library ภายนอก

โค้ดต้องผ่าน test เหล่านี้:
- ขายหลายรายการสำเร็จ คืนยอดคงเหลือถูกต้องทุกรายการ
- ถ้ารายการที่ 2 stock ไม่พอ หรือไม่มีสินค้า ต้องไม่หักรายการที่ 1 (State ไม่เปลี่ยนแปลง / Rollback สมบูรณ์)
```

### ผลลัพธ์โค้ดที่ AI สร้างขึ้น (รอบที่ 2):
```python
    def sell_many(self, orders: dict[str, int]) -> dict[str, int]:
        """
        ขายหลายรายการพร้อมกันในลักษณะ Atomic Transaction
        คืนค่า dict ของ {ชื่อสินค้า: ยอดคงเหลือหลังการขาย}
        หากมีรายการใดผิดพลาด จะไม่หักยอดสินค้าใด ๆ เลย
        """
        if not orders:
            return {}

        # ขั้นตอนที่ 1: ตรวจสอบความถูกต้องของคำสั่งซื้อทุกรายการก่อนเริ่มตัดสต็อก (Pre-validation)
        for name, amount in orders.items():
            if name not in self._items:
                raise KeyError(f"ไม่พบสินค้า '{name}' ในระบบ")
            if amount <= 0:
                raise ValueError("จำนวนที่ขายต้องมากกว่าศูนย์")
            if self._items[name].quantity < amount:
                raise ValueError(
                    f"สินค้า '{name}' คงเหลือ {self._items[name].quantity} ชิ้น "
                    f"ไม่เพียงพอสำหรับการขาย {amount} ชิ้น"
                )

        # ขั้นตอนที่ 2: เมื่อทุกรายการผ่านการตรวจสอบ จึงดำเนินการตัดสต็อก (Atomic Execution)
        results = {}
        for name, amount in orders.items():
            self._items[name].quantity -= amount
            results[name] = self._items[name].quantity

        return results
```

---

## 4. บทสรุปและวิเคราะห์ผลการทดลอง

### ผลลัพธ์ของทั้งสองรอบต่างกันอย่างไร?
1. **ความถูกต้องเชิงตรรกะและสถาปัตยกรรม (Correctness & Atomicity):**  
   - ในรอบแรก โค้ดขาดคุณสมบัติ Atomicity โดยสิ้นเชิง ตัดสต็อกไปทีละตัว ทำให้เกิดข้อมูลตกค้าง (State Inconsistency) เมื่อเกิดข้อผิดพลาดกลางทาง  
   - ในรอบที่สอง โค้ดแบ่งการทำงานเป็น 2 เฟสอย่างชัดเจน คือ **Pre-validation Phase** (ตรวจสอบสินค้าทุกตัวจนมั่นใจว่าพอ) และ **Execution Phase** (ตัดสต็อกพร้อมกัน) ทำให้คงคุณสมบัติ All-or-Nothing ได้ 100%
2. **ความเข้ากันได้กับระบบเดิม (System Integration):**  
   - โค้ดรอบที่สองถูกสร้างให้เป็นเมธอดของคลาส `Inventory` โดยตรง สามารถเข้าถึง `self._items` และยึดตาม Data Contract และ Exception Convention (`KeyError`, `ValueError`) เดิมของระบบ ทำให้สามารถนำไปรวมเข้ากับโค้ดหลักได้ทันทีโดยไม่มี Regression

### อะไรทำให้ผลลัพธ์ต่างกัน?
- **การป้อน Context ที่เฉพาะเจาะจง (Context Injection):** LLM ทำงานโดยการพยากรณ์ Token ถัดไปตามบริบทที่ได้รับ หากไม่มีบริบท LLM จะสร้างคำตอบทั่วไป (Generic Code) ตามค่าเฉลี่ยของข้อมูลในชุดฝึก ซึ่งมักละเลยความต้องการเฉพาะของโปรเจกต์
- **การกำหนด System Constraints & Test Expectations:** เมื่อเราระบุเงื่อนไข "ห้ามหักรายการใดเลยหากตัวที่ 2 ไม่พอ" พร้อมแนบโครงสร้างของ `InventoryItem` และประเภท Exception ทำให้ Attention Mechanism ของโมเดลโฟกัสไปที่ตรรกะการตรวจสอบล่วงหน้า (Two-phase validation) ส่งผลให้โค้ดที่สร้างขึ้นมีความถูกต้อง ปลอดภัย และพร้อมใช้งานในระดับ Production ทันที
