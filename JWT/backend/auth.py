import jwt
import datetime
import uuid
import time
from functools import wraps
from flask import request, jsonify
from config import Config
from database import get_db_connection

def _get_token_from_header():
    """Lấy token từ header Authorization"""
    if 'Authorization' in request.headers:
        auth_header = request.headers['Authorization']
        if isinstance(auth_header, str) and auth_header.startswith('Bearer '):
            return auth_header.split(' ')[1]
    return None

def _is_access_token_blacklisted(jti: str) -> bool:
    """Kiểm tra access token (jti) đã bị thu hồi chưa"""
    if not jti:
        return False
    conn = get_db_connection()
    row = conn.execute(
        "SELECT 1 FROM access_token_blacklist WHERE jti = ? LIMIT 1",
        (jti,)
    ).fetchone()
    conn.close()
    return row is not None

def blacklist_access_token(jti: str, exp_ts: int):
    """Thêm access token jti vào blacklist cho tới khi hết hạn"""
    if not jti:
        return
    conn = get_db_connection()
    try:
        conn.execute(
            "INSERT OR IGNORE INTO access_token_blacklist (jti, expires_at) VALUES (?, ?)",
            (jti, exp_ts)
        )
        conn.commit()
    finally:
        conn.close()

def _store_refresh_token(jti: str, user_id: int, expires_at: int):
    conn = get_db_connection()
    try:
        conn.execute(
            "INSERT OR IGNORE INTO refresh_tokens (jti, user_id, expires_at, revoked) VALUES (?, ?, ?, 0)",
            (jti, user_id, expires_at)
        )
        conn.commit()
    finally:
        conn.close()

def revoke_refresh_token(jti: str):
    conn = get_db_connection()
    try:
        conn.execute("UPDATE refresh_tokens SET revoked = 1 WHERE jti = ?", (jti,))
        conn.commit()
    finally:
        conn.close()

def generate_tokens(user_id, username, role, scopes=None):
    """Tạo cặp (access_token, refresh_token) với scopes và lưu refresh jti vào DB"""
    now = datetime.datetime.utcnow()
    if scopes is None:
        # Gán scopes theo role, có thể tuỳ biến
        if role == 'admin':
            scopes = ["read:books", "write:books", "manage:users", "read:stats", "borrow:write"]
        else:
            scopes = ["read:books", "borrow:write"]

    # Access token có jti để có thể blacklist khi logout
    access_jti = str(uuid.uuid4())
    access_payload = {
        'user_id': user_id,
        'username': username,
        'role': role,
        'scopes': scopes,
        'jti': access_jti,
        'exp': now + datetime.timedelta(seconds=Config.JWT_ACCESS_TOKEN_EXPIRES),
        'iat': now
    }
    access_token = jwt.encode(access_payload, Config.JWT_SECRET_KEY, algorithm='HS256')

    # Refresh token (dùng để xin lại access token), lưu vào DB theo jti
    refresh_jti = str(uuid.uuid4())
    refresh_exp_ts = int(time.time()) + int(Config.JWT_REFRESH_TOKEN_EXPIRES)
    refresh_payload = {
        'user_id': user_id,
        'type': 'refresh',
        'jti': refresh_jti,
        'exp': now + datetime.timedelta(seconds=Config.JWT_REFRESH_TOKEN_EXPIRES),
        'iat': now
    }
    refresh_token = jwt.encode(refresh_payload, Config.JWT_SECRET_KEY, algorithm='HS256')
    _store_refresh_token(refresh_jti, user_id, refresh_exp_ts)

    return access_token, refresh_token

def decode_token(token):
    """Giải mã JWT token"""
    try:
        payload = jwt.decode(token, Config.JWT_SECRET_KEY, algorithms=['HS256'])
        # Nếu là access token đã bị blacklist thì coi như không hợp lệ
        if payload.get('jti') and _is_access_token_blacklisted(payload.get('jti')):
            return None
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def decode_refresh_token(token):
    """Giải mã refresh token và xác thực thông tin trong DB"""
    try:
        payload = jwt.decode(token, Config.JWT_SECRET_KEY, algorithms=['HS256'])
        if payload.get('type') != 'refresh':
            return None
        jti = payload.get('jti')
        user_id = payload.get('user_id')
        if not jti or not user_id:
            return None
        conn = get_db_connection()
        row = conn.execute(
            "SELECT user_id, revoked, expires_at FROM refresh_tokens WHERE jti = ?",
            (jti,)
        ).fetchone()
        conn.close()
        if not row or row['user_id'] != user_id:
            return None
        if row['revoked'] == 1 or row['expires_at'] < int(time.time()):
            return None
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def token_required(f):
    """Decorator kiểm tra token hợp lệ"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = _get_token_from_header()
        
        if not token:
            return jsonify({'status': 'error', 'message': 'Token is missing'}), 401
        
        # Giải mã token
        payload = decode_token(token)
        if not payload:
            return jsonify({'status': 'error', 'message': 'Token is invalid or expired'}), 401
        
        # Truyền thông tin user vào function
        return f(payload, *args, **kwargs)
    
    return decorated

def admin_required(f):
    """Decorator kiểm tra quyền admin"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = _get_token_from_header()
        
        if not token:
            return jsonify({'status': 'error', 'message': 'Token is missing'}), 401
        
        # Giải mã token
        payload = decode_token(token)
        if not payload:
            return jsonify({'status': 'error', 'message': 'Token is invalid or expired'}), 401
        
        # Kiểm tra role admin
        if payload.get('role') != 'admin':
            return jsonify({'status': 'error', 'message': 'Admin access required'}), 403
        
        # Truyền thông tin user vào function
        return f(payload, *args, **kwargs)
    
    return decorated

def user_required(f):
    """Decorator kiểm tra quyền user (user hoặc admin đều được)"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = _get_token_from_header()
        
        if not token:
            return jsonify({'status': 'error', 'message': 'Token is missing'}), 401
        
        # Giải mã token
        payload = decode_token(token)
        if not payload:
            return jsonify({'status': 'error', 'message': 'Token is invalid or expired'}), 401
        
        # User hoặc admin đều có thể truy cập
        if payload.get('role') not in ['user', 'admin']:
            return jsonify({'status': 'error', 'message': 'User access required'}), 403
        
        # Truyền thông tin user vào function
        return f(payload, *args, **kwargs)
    
    return decorated

def requires_scope(scope: str):
    """Decorator kiểm tra scope trong access token (admin bypass)."""
    def decorator(f):
        @wraps(f)
        @token_required
        def wrapper(payload, *args, **kwargs):
            if payload.get('role') == 'admin':
                return f(payload, *args, **kwargs)
            scopes = payload.get('scopes', [])
            if scope in scopes:
                return f(payload, *args, **kwargs)
            return jsonify({'status': 'error', 'message': 'Insufficient scope'}), 403
        return wrapper
    return decorator
