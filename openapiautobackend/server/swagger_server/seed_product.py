from swagger_server.db import products_collection
from datetime import datetime, timezone

# 20 sản phẩm mẫu đa dạng danh mục
sample_products = [
    # 1–5: Electronics
    {
        "sku": "APP-PHN-001",
        "name": "iPhone 15 Pro",
        "category": "Electronics",
        "brand": "Apple",
        "price": 1099.99,
        "quantity": 30,
        "status": "active",
        "description": "Flagship smartphone with A17 Pro chip.",
        "image_url": "https://example.com/iphone15pro.jpg"
    },
    {
        "sku": "SAM-PHN-002",
        "name": "Samsung Galaxy S24 Ultra",
        "category": "Electronics",
        "brand": "Samsung",
        "price": 999.99,
        "quantity": 50,
        "status": "active",
        "description": "High-end Android smartphone with S Pen support.",
        "image_url": "https://example.com/galaxy-s24ultra.jpg"
    },
    {
        "sku": "XIA-PHN-003",
        "name": "Xiaomi 14 Pro",
        "category": "Electronics",
        "brand": "Xiaomi",
        "price": 699.99,
        "quantity": 100,
        "status": "active",
        "description": "Affordable flagship phone with Snapdragon 8 Gen 3.",
        "image_url": "https://example.com/xiaomi14pro.jpg"
    },
    {
        "sku": "SON-HPH-004",
        "name": "Sony WH-1000XM5",
        "category": "Audio",
        "brand": "Sony",
        "price": 349.99,
        "quantity": 80,
        "status": "active",
        "description": "Noise-cancelling wireless headphones with 30-hour battery.",
        "image_url": "https://example.com/sony-xm5.jpg"
    },
    {
        "sku": "JBL-SPK-005",
        "name": "JBL Charge 5 Speaker",
        "category": "Audio",
        "brand": "JBL",
        "price": 149.99,
        "quantity": 60,
        "status": "active",
        "description": "Portable waterproof Bluetooth speaker with deep bass.",
        "image_url": "https://example.com/jbl-charge5.jpg"
    },

    # 6–10: Laptops
    {
        "sku": "APP-LAP-006",
        "name": "MacBook Air M3",
        "category": "Laptops",
        "brand": "Apple",
        "price": 1299.99,
        "quantity": 25,
        "status": "active",
        "description": "Lightweight laptop powered by Apple Silicon M3 chip.",
        "image_url": "https://example.com/macbookair-m3.jpg"
    },
    {
        "sku": "DEL-LAP-007",
        "name": "Dell XPS 13 Plus",
        "category": "Laptops",
        "brand": "Dell",
        "price": 1399.99,
        "quantity": 35,
        "status": "active",
        "description": "Premium ultrabook with InfinityEdge OLED display.",
        "image_url": "https://example.com/dell-xps13.jpg"
    },
    {
        "sku": "HP-LAP-008",
        "name": "HP Spectre x360",
        "category": "Laptops",
        "brand": "HP",
        "price": 1249.99,
        "quantity": 40,
        "status": "active",
        "description": "Convertible 2-in-1 laptop with touchscreen and pen.",
        "image_url": "https://example.com/hp-spectre.jpg"
    },
    {
        "sku": "LEN-LAP-009",
        "name": "Lenovo ThinkPad X1 Carbon Gen 11",
        "category": "Laptops",
        "brand": "Lenovo",
        "price": 1499.99,
        "quantity": 20,
        "status": "active",
        "description": "Durable business laptop with long battery life.",
        "image_url": "https://example.com/thinkpad-x1.jpg"
    },
    {
        "sku": "ASU-LAP-010",
        "name": "ASUS ROG Zephyrus G14",
        "category": "Laptops",
        "brand": "ASUS",
        "price": 1799.99,
        "quantity": 15,
        "status": "active",
        "description": "Powerful gaming laptop with Ryzen 9 CPU and RTX GPU.",
        "image_url": "https://example.com/rog-g14.jpg"
    },

    # 11–15: Home Appliances
    {
        "sku": "PHI-TV-011",
        "name": "Philips 4K Smart TV 55 inch",
        "category": "Home Appliances",
        "brand": "Philips",
        "price": 599.99,
        "quantity": 18,
        "status": "active",
        "description": "Ambilight smart TV with Android OS and 4K HDR.",
        "image_url": "https://example.com/philips-tv.jpg"
    },
    {
        "sku": "SAM-TV-012",
        "name": "Samsung QLED Q80C 65 inch",
        "category": "Home Appliances",
        "brand": "Samsung",
        "price": 1299.99,
        "quantity": 12,
        "status": "active",
        "description": "QLED TV with quantum processor and Dolby Atmos sound.",
        "image_url": "https://example.com/samsung-q80c.jpg"
    },
    {
        "sku": "LG-REF-013",
        "name": "LG InstaView Door-in-Door Refrigerator",
        "category": "Home Appliances",
        "brand": "LG",
        "price": 1999.99,
        "quantity": 8,
        "status": "active",
        "description": "Smart refrigerator with touch glass door and Wi-Fi.",
        "image_url": "https://example.com/lg-fridge.jpg"
    },
    {
        "sku": "PAN-MIC-014",
        "name": "Panasonic Inverter Microwave Oven",
        "category": "Home Appliances",
        "brand": "Panasonic",
        "price": 229.99,
        "quantity": 25,
        "status": "active",
        "description": "Compact inverter microwave with smart sensor.",
        "image_url": "https://example.com/panasonic-microwave.jpg"
    },
    {
        "sku": "PHI-AIR-015",
        "name": "Philips Air Purifier Series 3000i",
        "category": "Home Appliances",
        "brand": "Philips",
        "price": 349.99,
        "quantity": 40,
        "status": "active",
        "description": "Smart air purifier with real-time air quality display.",
        "image_url": "https://example.com/philips-airpurifier.jpg"
    },

    # 16–20: Accessories
    {
        "sku": "APP-WAT-016",
        "name": "Apple Watch Series 9",
        "category": "Wearables",
        "brand": "Apple",
        "price": 449.99,
        "quantity": 60,
        "status": "active",
        "description": "Advanced smartwatch with health tracking and GPS.",
        "image_url": "https://example.com/apple-watch9.jpg"
    },
    {
        "sku": "FIT-WAT-017",
        "name": "Fitbit Charge 6",
        "category": "Wearables",
        "brand": "Fitbit",
        "price": 159.99,
        "quantity": 75,
        "status": "active",
        "description": "Fitness tracker with heart rate and sleep monitoring.",
        "image_url": "https://example.com/fitbit-charge6.jpg"
    },
    {
        "sku": "LOG-MOU-018",
        "name": "Logitech MX Master 3S",
        "category": "Accessories",
        "brand": "Logitech",
        "price": 119.99,
        "quantity": 100,
        "status": "active",
        "description": "Wireless ergonomic mouse with fast scroll and Bluetooth.",
        "image_url": "https://example.com/mx-master3s.jpg"
    },
    {
        "sku": "KIN-KBD-019",
        "name": "Keychron K6 Wireless Keyboard",
        "category": "Accessories",
        "brand": "Keychron",
        "price": 89.99,
        "quantity": 120,
        "status": "active",
        "description": "Compact mechanical keyboard with RGB and Bluetooth.",
        "image_url": "https://example.com/keychron-k6.jpg"
    },
    {
        "sku": "ANK-PWR-020",
        "name": "Anker PowerCore 20000 PD",
        "category": "Accessories",
        "brand": "Anker",
        "price": 69.99,
        "quantity": 200,
        "status": "active",
        "description": "Portable power bank with fast charging and USB-C PD.",
        "image_url": "https://example.com/anker-powercore.jpg"
    },
]

# Thêm thời gian tạo và cập nhật
now = datetime.now(timezone.utc).isoformat()
for product in sample_products:
    product["created_at"] = now
    product["updated_at"] = now

# Ghi vào MongoDB
result = products_collection.insert_many(sample_products)
print(f"Đã thêm {len(result.inserted_ids)} sản phẩm mẫu vào MongoDB!")
