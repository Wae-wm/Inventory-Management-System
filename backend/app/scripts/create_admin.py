"""สร้างผู้ใช้ Admin คนแรก  รันด้วย:  python -m app.scripts.create_admin"""
from getpass import getpass

from app.database import SessionLocal
from app.services.users import create_user


def main() -> None:
    username = input("username: ").strip()
    full_name = input("ชื่อ-นามสกุล: ").strip()
    password = getpass("รหัสผ่าน (ตัวอักษรไม่แสดงบนจอ): ")
    if len(password) < 8:
        raise SystemExit("รหัสผ่านต้องยาวอย่างน้อย 8 ตัวอักษร")
    if password != getpass("พิมพ์รหัสผ่านอีกครั้ง: "):
        raise SystemExit("รหัสผ่านสองครั้งไม่ตรงกัน")

    with SessionLocal() as db:
        user = create_user(
            db, username=username, full_name=full_name, password=password, role="ADMIN"
        )
        print(f"สร้าง Admin สำเร็จ: {user.username} (user_id={user.user_id})")


if __name__ == "__main__":
    main()
