import random
import time
from locust import HttpUser, task, between
from json.decoder import JSONDecodeError

class BaseAuthUser(HttpUser):
    host = "http://127.0.0.1:8080"
    wait_time = between(1, 3) 
    
    # Đánh dấu đây là abstract class - Locust sẽ KHÔNG chạy class này
    abstract = True
    access_token = None
    product_id_created = None
    
    # Thông tin đăng nhập
    credentials = {}

    def on_start(self):
        """Hàm được gọi khi một người dùng ảo mới bắt đầu (Login)"""
        if not self.access_token:
            self.login()
        
    def login(self):
        """Thực hiện POST /api/sessions để lấy token"""
        login_data = self.credentials
        
        try:
            with self.client.post("/api/sessions", json=login_data, name="/api/sessions [POST/Login]", catch_response=True) as response:
                if response.status_code == 200:
                    json_response = response.json()
                    self.access_token = json_response['data']['access_token']
                    # Thiết lập header Authorization cho tất cả request tiếp theo
                    self.client.headers = {"Authorization": f"Bearer {self.access_token}"}
                    print(f"[{self.credentials['username']}] Login OK. Token acquired.")
                    response.success()
                else:
                    response.failure(f"Login Failed with status {response.status_code}")
                    # Dừng user này thay vì quit toàn bộ test
                    raise Exception(f"Login failed for {self.credentials['username']}")
        except JSONDecodeError:
            print("Login Failed: Could not decode JSON response.")
            raise Exception(f"Login JSON decode failed for {self.credentials['username']}")



# --- 1. ADMIN USER (Full Access) ---
class AdminUser(BaseAuthUser):
    weight = 8
    credentials = {"username": "admin", "password": "admin123"}
    product_counter = 0

    @task(3)
    def view_products(self):
        """GET /api/products (UserProducts & AdminProducts)"""
        self.client.get(f"/api/products?page={random.randint(1, 2)}&limit=20", name="/api/products [GET]")

    @task(1)
    def create_product(self):
        """POST /api/products (AdminProducts)"""
        AdminUser.product_counter += 1
        
        new_sku = f"PROD-LOAD-{AdminUser.product_counter}-{random.randint(100, 999)}"
        payload = {
            "sku": new_sku,
            "name": f"Load Test Product {AdminUser.product_counter}",
            "category": random.choice(["Electronics", "Home", "Tools", "Software"]),
            "price": round(random.uniform(10.0, 500.0), 2),
            "quantity": random.randint(1, 100),
            "brand": "Acme Inc."
        }
        
        with self.client.post("/api/products", json=payload, name="/api/products [POST/Create]", catch_response=True) as response:
            if response.status_code == 201:
                try:
                    # Lưu Product ID để sử dụng trong task update/delete
                    AdminUser.product_id_created = response.json()['data']['id']
                    response.success()
                except (KeyError, JSONDecodeError):
                    response.failure("Product created but failed to get ID from response.")
            
    @task(2)
    def get_statistics(self):
        """GET /api/statistics (AdminStatistics)"""
        self.client.get("/api/statistics", name="/api/statistics [GET]")


# --- 2. USER USER (View Only) ---
class NormalUser(BaseAuthUser):
    weight = 2
    credentials = {"username": "user", "password": "user123"}
    SAMPLE_PRODUCT_IDS = [
        "690a23ff6f7edf67a0b8973f",
        "690a23ff6f7edf67a0b89740",
        "690a23ff6f7edf67a0b89742",
        "690a23ff6f7edf67a0b89743",
        "690a23ff6f7edf67a0b89744"
    ]

    @task(5)
    def view_products_list(self):
        """GET /api/products (UserProducts)"""
        self.client.get(f"/api/products?sort=price_desc&category=Electronics", name="/api/products [GET/List]")

    @task(3)
    def get_product_detail(self):
        """GET /api/products/{product_id} (UserProducts)"""
        product_id = random.choice(self.SAMPLE_PRODUCT_IDS)
        self.client.get(f"/api/products/{product_id}", name="/api/products/{id} [GET/Detail]")

    @task(1)
    def get_categories(self):
        """GET /api/categories (UserProducts)"""
        self.client.get("/api/categories", name="/api/categories [GET/Categories]")
