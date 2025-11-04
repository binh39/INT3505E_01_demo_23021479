from swagger_server.db import users_collection
from datetime import datetime, timezone
import hashlib

def hash_password(password: str) -> str:
    """Băm mật khẩu bằng SHA256 (đơn giản cho demo)"""
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

def seed_users():
    now = datetime.now(timezone.utc).isoformat()

    users = [
        {
            "username": "admin",
            "password": hash_password("admin123"),
            "role": "admin",
            "created_at": now,
            "updated_at": now,
        },
        {
            "username": "user",
            "password": hash_password("user123"),
            "role": "user",
            "created_at": now,
            "updated_at": now,
        },
    ]

    # Xóa user cũ nếu tồn tại để tránh trùng
    for u in users:
        users_collection.delete_many({"username": u["username"]})

    # Thêm mới
    result = users_collection.insert_many(users)
    print(f"Đã thêm {len(result.inserted_ids)} tài khoản mẫu vào MongoDB!")
    print("admin / admin123")
    print("user / user123")

if __name__ == "__main__":
    seed_users()
