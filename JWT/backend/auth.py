import jwt
import datetime
from functools import wraps
from flask import request, jsonify
from config import Config
from database import get_db_connection

def generate_token(user_id, username, role):
    """Tạo JWT token"""
    payload = {
        'user_id': user_id,
        'username': username,
        'role': role,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(seconds=Config.JWT_ACCESS_TOKEN_EXPIRES),
        'iat': datetime.datetime.utcnow()
    }
    token = jwt.encode(payload, Config.JWT_SECRET_KEY, algorithm='HS256')
    return token

def decode_token(token):
    """Giải mã JWT token"""
    try:
        payload = jwt.decode(token, Config.JWT_SECRET_KEY, algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def token_required(f):
    """Decorator kiểm tra token hợp lệ"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        # Lấy token từ header Authorization
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            if auth_header.startswith('Bearer '):
                token = auth_header.split(' ')[1]
        
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
        token = None
        
        # Lấy token từ header Authorization
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            if auth_header.startswith('Bearer '):
                token = auth_header.split(' ')[1]
        
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
        token = None
        
        # Lấy token từ header Authorization
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            if auth_header.startswith('Bearer '):
                token = auth_header.split(' ')[1]
        
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
