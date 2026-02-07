# ระบบคำนวณเงินเยียวยาของรัฐ

โปรเจกต์นี้เป็นส่วนหนึ่งของการสอบปฏิบัติการเขียนโปรแกรมแบบ MVC พัฒนาด้วยภาษา **Python** โดยใช้ **Flask Framework** ตามสถาปัตยกรรม **MVC (Model-View-Controller)**

---

## สิ่งที่ต้องเตรียม

- **Python 3.8** หรือสูงกว่า
- **Git**

---

## การติดตั้งและตั้งค่า

1.  **Clone โปรเจกต์**

    ```bash
    git clone https://github.com/SaveKit/MVC2-2568.git
    cd MVC2-2568
    ```

2.  **สร้างและใช้งาน Virtual Environment (แนะนำ)**
    เพื่อแยก Library ไม่ให้ปนกับเครื่องหลัก
    - **Windows**
      ```bash
      python -m venv venv
      .\venv\Scripts\activate
      ```
    - **Mac / Linux**
      ```bash
      python3 -m venv venv
      source venv/bin/activate
      ```

3.  **ติดตั้ง Library ที่จำเป็น**

    ```bash
    pip install -r requirements.txt
    ```

4.  **ตั้งค่าความปลอดภัย (.env)**
    สร้างไฟล์ชื่อ `.env` ที่โฟลเดอร์หลัก (ระดับเดียวกับ `main.py`) และใส่ค่า Secret Key สำหรับ Session
    ```text
    SECRET_KEY=exam_super_secret_key_2026
    ```

---

## การจัดการฐานข้อมูล

ระบบใช้ **SQLite** เป็นฐานข้อมูล โดยมีสคริปต์เตรียมไว้ให้พร้อมใช้งาน

### 1. เริ่มต้นสร้างฐานข้อมูล

รันคำสั่งนี้เพื่อสร้างไฟล์ `relief_fund.db` และตารางที่จำเป็นทั้งหมด (Claimants, Claims, Policies, Compensations, Users)

```bash
python database/db_setup.py
```

### 2. (Optional) เพิ่มข้อมูลทดสอบ (Seed Data)

หากต้องการข้อมูลตัวอย่างเพื่อทดสอบเงื่อนไขการคำนวณ (รายได้น้อย, ทั่วไป, รายได้สูง) ให้รันคำสั่ง

```bash
python seed_data.py
```

ระบบจะทำการล้างข้อมูลการคำนวณเก่าและเพิ่มข้อมูลทดสอบให้ทันที 5 เคส

---

## การรันโปรแกรม

1.  **เริ่มเซิร์ฟเวอร์**
    รันคำสั่งที่ Root Directory ของโปรเจกต์

    ```bash
    python main.py
    ```

    _หน้าจอจะแสดงข้อความ: `Server starting at http://127.0.0.1:5000`_

2.  **เข้าใช้งาน**
    เปิด Web Browser แล้วไปที่ URL
    - `http://127.0.0.1:5000`

---

## ข้อมูลเข้าสู่ระบบ

ระบบได้จำลองผู้ใช้งานไว้ 2 ระดับตามข้อกำหนดของโจทย์

| Role (สิทธิ์)             | Username | Password | หน้าที่และการเข้าถึง                                                                          |
| :------------------------ | :------- | :------- | :-------------------------------------------------------------------------------------------- |
| **Officer** (เจ้าหน้าที่) | `admin`  | `1234`   | **เข้าถึงหน้ารายการ (Dashboard)** ดูรายชื่อผู้ยื่นคำขอ, สถานะ, และยอดเงินเยียวยาที่คำนวณแล้ว |
| **Citizen** (ประชาชน)     | `user`   | `1234`   | **เข้าถึงหน้าแบบฟอร์ม (Form)** กรอกข้อมูลส่วนตัวและรายได้เพื่อยื่นคำขอ                       |

---

## โครงสร้างโปรเจกต์และหน้าที่

โปรเจกต์นี้ถูกออกแบบตามสถาปัตยกรรม **Model-View-Controller (MVC)** เพื่อแยกส่วนการทำงานอย่างชัดเจน

### 1. Models (`models/`)

ทำหน้าที่จัดการ **Business Logic** และกฎการคำนวณเงินเยียวยา โดยไม่ยุ่งเกี่ยวกับ Database หรือ View

- **ไฟล์:** `models/claim_models.py`
- **การทำงาน:** แยกคลาสการคำนวณเป็น 3 รูปแบบตามโจทย์
  - `ClaimModel`: คำนวณแบบทั่วไป (General)
  - `LowIncomeClaimModel`: คำนวณแบบผู้มีรายได้น้อย (Low Income)
  - `HighIncomeClaimModel`: คำนวณแบบผู้มีรายได้สูง (High Income)

### 2. Views (`templates/`)

ทำหน้าที่แสดงผล User Interface (UI) ให้กับผู้ใช้

- `layout.html`: โครงสร้างหลักของหน้าเว็บ (Navbar, Flash Messages)
- `login.html`: หน้าจอเข้าสู่ระบบ
- `index.html`: หน้าจอแสดงตารางรายการคำขอ (สำหรับ Officer)
- `form.html`: หน้าจอแบบฟอร์มกรอกข้อมูล (สำหรับ Citizen)

### 3. Controllers (`controllers/`)

ทำหน้าที่เป็นตัวกลางรับ Request จากผู้ใช้, เรียก Model มาประมวลผล, และส่งข้อมูลไปแสดงที่ View

- **`auth_controller.py` (Blueprint: auth):**
  - จัดการ Authentication (Login/Logout)
  - ตรวจสอบ Username/Password และกำหนด Session Role
- **`claim_controller.py` (Blueprint: claim):**
  - จัดการ Flow การทำงานหลัก
  - รับค่า Input -> เรียก Model คำนวณ -> บันทึกลง Database -> Redirect

### 4. Utils & Database

- **`utils/db.py`:** ฟังก์ชันกลางสำหรับเชื่อมต่อ SQLite Database
- **`database/db_setup.py`:** สคริปต์สำหรับสร้างตาราง (Schema) และข้อมูลเริ่มต้น

---

## สรุป Routes และ Actions หลัก

| Route     | Method     | Controller | รายละเอียดการทำงาน                                                               |
| :-------- | :--------- | :--------- | :------------------------------------------------------------------------------- |
| `/login`  | `GET/POST` | Auth       | ตรวจสอบสิทธิ์และสร้าง Session เพื่อแยกผู้ใช้ออกเป็น Officer หรือ Citizen         |
| `/logout` | `GET`      | Auth       | ล้างค่า Session และส่งกลับหน้า Login                                             |
| `/`       | `GET`      | Claim      | **(Officer Only)** ดึงข้อมูลจากตาราง Claims/Compensations มาแสดงผล               |
| `/create` | `GET`      | Claim      | **(Citizen Only)** แสดงแบบฟอร์มรับข้อมูล                                         |
| `/submit` | `POST`     | Claim      | รับค่าฟอร์ม > ดึง Policy > **คำนวณยอดเงิน (Model)** > บันทึกข้อมูล > แสดงผลลัพธ์ |

---

**ผู้จัดทำ:** นายกิตติพิชญ์ มุกดาสนิท
**รหัสนักศึกษา:** 65050075
