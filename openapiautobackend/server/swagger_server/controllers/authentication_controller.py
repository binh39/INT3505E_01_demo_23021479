import connexion
import six
import jwt
import uuid
import hashlib
from datetime import datetime, timedelta, timezone
from functools import wraps

from swagger_server.models.error import Error  # noqa: E501
from swagger_server.models.inline_response200 import InlineResponse200  # noqa: E501
from swagger_server.models.inline_response2001 import InlineResponse2001  # noqa: E501
from swagger_server.models.inline_response2002 import InlineResponse2002  # noqa: E501
from swagger_server.models.login_request import LoginRequest  # noqa: E501
from swagger_server.models.login_response import LoginResponse  # noqa: E501
from swagger_server.models.logout_request import LogoutRequest  # noqa: E501
from swagger_server.models.refresh_request import RefreshRequest  # noqa: E501
from swagger_server.models.refresh_response import RefreshResponse  # noqa: E501
from swagger_server import util

from swagger_server.db import users_collection, refresh_tokens_collection, blacklist_collection

# JWT Configuration
SECRET_KEY = "secret-key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 5
REFRESH_TOKEN_EXPIRE_MINUTES = 60

def hash_password(password: str) -> str:
    """Băm mật khẩu bằng SHA256 (đơn giản cho demo)"""
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

def create_access_token(user_id, username, role):
    """Create JWT access token"""
    now = datetime.now(timezone.utc)
    expire = now + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    # Define scopes based on role
    scopes = []
    if role == "admin":
        scopes = ["read:products", "write:products", "manage:inventory", "read:stats"]
    elif role == "user":
        scopes = ["read:products"]
    
    payload = {
        "user_id": user_id,
        "username": username,
        "role": role,
        "scopes": scopes,
        "jti": str(uuid.uuid4()),  # JWT ID for blacklist
        "exp": expire,
        "iat": now
    }
    
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return token, int(expire.timestamp())


def create_refresh_token(user_id):
    """Create refresh token"""
    now = datetime.now(timezone.utc)
    expire = now + timedelta(minutes=REFRESH_TOKEN_EXPIRE_MINUTES)
    
    payload = {
        "user_id": user_id,
        "type": "refresh",
        "jti": str(uuid.uuid4()),
        "exp": expire,
        "iat": now
    }
    
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    
    # Store refresh token in database
    refresh_tokens_collection.insert_one({
        "jti": payload["jti"],
        "user_id": user_id,
        "token": token,
        "created_at": now.isoformat(),
        "expires_at": expire.isoformat(),
        "revoked": False
    })
    
    return token, int(expire.timestamp())


def verify_token(token):
    """Verify JWT token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        if blacklist_collection.find_one({"jti": payload.get("jti")}):
            return None, "Token has been revoked"
        
        return payload, None
    except jwt.ExpiredSignatureError:
        return None, "Token has expired"
    except jwt.InvalidTokenError:
        return None, "Invalid token"


# DELETE /api/sessions - Logout
def api_sessions_delete(body=None):  # noqa: E501
    try:
        # Get access token from Authorization header
        auth_header = connexion.request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return {"status": "error", "message": "Missing or invalid Authorization header"}, 401
        
        access_token = auth_header.split(' ')[1]
        
        # Verify access token
        payload, error = verify_token(access_token)
        if error:
            return {"status": "error", "message": error}, 401
        
        # Blacklist the access token (until it expires naturally)
        jti = payload.get("jti")
        exp = payload.get("exp")
        if jti:
            blacklist_collection.insert_one({
                "jti": jti,
                "token": access_token,
                "blacklisted_at": datetime.now(timezone.utc).isoformat(),
                "expires_at": datetime.fromtimestamp(exp, tz=timezone.utc).isoformat()
            })
        
        # Revoke refresh token if provided in body
        if connexion.request.is_json and body is not None:
            body = LogoutRequest.from_dict(connexion.request.get_json())  # noqa: E501
            refresh_token = body.refresh_token if hasattr(body, 'refresh_token') else None
            
            if refresh_token:
                try:
                    refresh_payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
                    refresh_jti = refresh_payload.get("jti")
                    
                    # Mark refresh token as revoked
                    refresh_tokens_collection.update_one(
                        {"jti": refresh_jti},
                        {"$set": {"revoked": True, "revoked_at": datetime.now(timezone.utc).isoformat()}}
                    )
                except:
                    pass  # Ignore invalid refresh token on logout
        
        return {
            "status": "success",
            "message": "Logged out successfully",
            "data": None,
            "links": {
                "login": {"href": "/api/sessions", "method": "POST"},
                "home": {"href": "/", "method": "GET"}
            },
            "meta": {
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        }, 200
        
    except Exception as e:
        return {"status": "error", "message": f"Internal server error: {str(e)}"}, 500


# GET /api/sessions/me - Verify token and get user info
def api_sessions_me_get():  # noqa: E501
    try:
        # Get access token from Authorization header
        auth_header = connexion.request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return {"status": "error", "message": "Missing or invalid Authorization header"}, 401
        
        access_token = auth_header.split(' ')[1]
        
        # Verify access token
        payload, error = verify_token(access_token)
        if error:
            return {"status": "error", "message": error}, 401
        
        # Get user info from payload
        user_info = {
            "id": payload.get("user_id"),
            "username": payload.get("username"),
            "role": payload.get("role")
        }
        
        # Calculate when token expires
        exp = payload.get("exp")
        token_expires_at = datetime.fromtimestamp(exp, tz=timezone.utc).isoformat() if exp else None
        
        return {
            "status": "success",
            "message": "Token is valid",
            "data": user_info,
            "links": {
                "self": {"href": "/api/sessions/me", "method": "GET"},
                "logout": {"href": "/api/sessions", "method": "DELETE"},
                "refresh": {"href": "/api/sessions/refresh", "method": "POST"},
                "products": {"href": "/api/products", "method": "GET"}
            },
            "meta": {
                "token_expires_at": token_expires_at,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        }, 200
        
    except Exception as e:
        return {"status": "error", "message": f"Internal server error: {str(e)}"}, 500


# POST /api/sessions - User login
def api_sessions_post(body):  # noqa: E501
    try:
        if not connexion.request.is_json:
            return {"status": "error", "message": "Request body must be JSON"}, 400
        
        login_req = LoginRequest.from_dict(connexion.request.get_json())
        username = getattr(login_req, "username", None)
        password = getattr(login_req, "password", None)
        
        if not username or not password:
            return {
                "status": "error", 
                "message": "Username and password are required",
                "meta": {"required_fields": ["username", "password"]}
            }, 400
        
        user = users_collection.find_one({"username": username})
        
        if not user:
            return {"status": "error", "message": "User not found"}, 401
        
        if user.get("password") != hash_password(password):
            return {"status": "error", "message": "Wrong password"}, 401
        
        user_id = user.get("user_id") or user.get("id")
        user_role = user.get("role", "user")
        
        access_token, access_exp = create_access_token(user_id, username, user_role)
        refresh_token, refresh_exp = create_refresh_token(user_id)
        
        links = {
            "self": {"href": "/api/sessions", "method": "POST"},
            "verify": {"href": "/api/sessions/me", "method": "GET"},
            "refresh": {"href": "/api/sessions/refresh", "method": "POST"},
            "logout": {"href": "/api/sessions", "method": "DELETE"},
            "products": {"href": "/api/products", "method": "GET"}
        }
        
        if user_role == "admin":
            links["statistics"] = {"href": "/api/statistics", "method": "GET"}
        
        return {
            "status": "success",
            "message": "Login successful",
            "data": {
                "id": user_id,
                "username": username,
                "role": user_role,
                "access_token": access_token,
                "refresh_token": refresh_token
            },
            "links": links,
            "meta": {
                "access_token_expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60,
                "refresh_token_expires_in": REFRESH_TOKEN_EXPIRE_MINUTES * 60,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        }, 200
        
    except Exception as e:
        return {"status": "error", "message": f"Internal server error: {str(e)}"}, 500


# POST /api/sessions/refresh - Refresh access token
def api_sessions_refresh_post(body):  # noqa: E501
    try:
        if not connexion.request.is_json:
            return {"status": "error", "message": "Request body must be JSON"}, 400
        
        body = RefreshRequest.from_dict(connexion.request.get_json())  # noqa: E501
        
        # Validate required field
        refresh_token = body.refresh_token if hasattr(body, 'refresh_token') else None
        
        if not refresh_token:
            return {
                "status": "error", 
                "message": "refresh_token is required",
                "meta": {"required_fields": ["refresh_token"]}
            }, 400
        
        # Verify refresh token
        try:
            payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        except jwt.ExpiredSignatureError:
            return {"status": "error", "message": "Refresh token has expired"}, 401
        except jwt.InvalidTokenError:
            return {"status": "error", "message": "Invalid refresh token"}, 401
        
        # Check token type
        if payload.get("type") != "refresh":
            return {"status": "error", "message": "Invalid token type"}, 401
        
        # Check if refresh token is revoked
        jti = payload.get("jti")
        refresh_token_doc = refresh_tokens_collection.find_one({"jti": jti})
        
        if not refresh_token_doc:
            return {"status": "error", "message": "Refresh token not found"}, 401
        
        if refresh_token_doc.get("revoked"):
            return {"status": "error", "message": "Refresh token has been revoked"}, 401
        
        # Get user info
        user_id = payload.get("user_id")
        user = users_collection.find_one({"user_id": user_id}) or users_collection.find_one({"id": user_id})
        
        if not user:
            return {"status": "error", "message": "User not found"}, 401
        
        username = user.get("username")
        role = user.get("role", "user")
        
        # Create new access token
        new_access_token, access_exp = create_access_token(user_id, username, role)
        
        return {
            "status": "success",
            "message": "Access token refreshed",
            "data": {
                "access_token": new_access_token
            },
            "links": {
                "self": {"href": "/api/sessions/refresh", "method": "POST"},
                "verify": {"href": "/api/sessions/me", "method": "GET"},
                "logout": {"href": "/api/sessions", "method": "DELETE"},
                "products": {"href": "/api/products", "method": "GET"}
            },
            "meta": {
                "access_token_expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        }, 200
        
    except Exception as e:
        return {"status": "error", "message": f"Internal server error: {str(e)}"}, 500


# GET / - Root endpoint
def root_get():  # noqa: E501
    try:
        return {
            "status": "success",
            "message": "Product Management System with JWT Authentication",
            "data": {
                "version": "1.0",
                "description": "RESTful API with JWT and HATEOAS",
                "features": [
                    "JWT Authentication with Access & Refresh tokens",
                    "Role-based Authorization (Admin/User)",
                    "Product Management (CRUD)",
                    "Inventory Statistics",
                    "HATEOAS principles"
                ]
            },
            "links": {
                "self": {"href": "/", "method": "GET"},
                "login": {"href": "/api/sessions", "method": "POST"},
                "products": {"href": "/api/products", "method": "GET"},
                "categories": {"href": "/api/products/categories", "method": "GET"},
                "documentation": {"href": "/ui", "method": "GET"}
            },
            "meta": {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "api_status": "operational"
            }
        }, 200
        
    except Exception as e:
        return {"status": "error", "message": f"Internal server error: {str(e)}"}, 500
