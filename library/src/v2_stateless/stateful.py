from flask import Flask, jsonify, session, request, Response

app = Flask(__name__)

app.config['SECRET_KEY'] = 'mot_key_bi_mat_rat_bao_mat'
app.config['SESSION_TYPE'] = 'filesystem'

# --- Dữ liệu giả lập ---
BOOK_DATA = {
    "user123": [
        {"book_key": "B001", "title": "Sức Mạnh Của Hiện Tại"},
        {"book_key": "B002", "title": "Nhà Giả Kim"},
    ],
    "user456": [
        {"book_key": "B010", "title": "Đắc Nhân Tâm"},
    ]
}

@app.route("/login/<user_id>", methods=["POST"])
def login(user_id):
    "Server lưu trạng thái (user_id)"
    if user_id in BOOK_DATA:
        session['user_id'] = user_id
        return jsonify({"message": f"Login success. User {user_id} has been saved."}, 200)
    return jsonify({"error": "User not found."}, 401)

@app.route("/api/books", methods=["GET"])
def get_books():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"error": "Unauthorized access. Server cannot find user session."}, 401)

    print(f"Get user_id '{user_id}' from session.")
    books = BOOK_DATA.get(user_id, [])
    return jsonify({"user_id": user_id, "books": books})

# CODE ON DEMAND

@app.route("/api/widget/promo", methods=["GET"])
def get_promo_code():
    "Code-On-Demand: Server trả về mã JavaScript thực thi"
    user_type = request.args.get('user_type')

    if user_type == 'premium':
        js_code = """
        function showPremiumPromo() {
            const promoDiv = document.getElementById('promo-message');
            promoDiv.innerHTML = '<div>Premium!</div>';
        }
        showPremiumPromo();
        """
    else:
        js_code = """
        function showBasicPromo() {
            const promoDiv = document.getElementById('promo-message');
            promoDiv.innerHTML = '<div>Cơ Bản</div>';
        }
        showBasicPromo();
        """
    
    # JavaScript code với Content-Type là application/javascript
    return Response(js_code, mimetype="application/javascript")
