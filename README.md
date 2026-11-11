# Inventory Management System

ระบบจัดการคลังสินค้าแบบ Full-Stack (React + FastAPI + MySQL)

## โครงสร้างโฟลเดอร์

- `backend/` โค้ด FastAPI
- `database/` ไฟล์ SQL สร้างตาราง (`schema.sql`)
- `docs/` เอกสาร และ ER Diagram

## เริ่มใช้งาน Backend

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate        # Windows  (macOS/Linux: source .venv/bin/activate)
pip install -r requirements.txt
copy .env.example .env        # แล้วแก้รหัสผ่าน MySQL ใน .env
uvicorn app.main:app --reload
```

เปิด http://127.0.0.1:8000/docs เพื่อดูและทดลอง API
