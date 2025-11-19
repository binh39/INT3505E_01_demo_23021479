# Payment API Versioning Demo

Demo API versioning cho hệ thống thanh toán đơn giản với Flask và SQLite.

# Tạo venv
python -m venv venv

# Kích hoạt venv
.\venv\Scripts\Activate

# Cài đặt dependencies
pip install -r requirements.txt

### 2. Khởi tạo database
python database.py

### 3. Chạy ứng dụng
python app.py

Server sẽ chạy tại: `http://localhost:5000`

# Chạy test script
python test_api.py

### Reset database
rm payments.db
python database.py
