from typing import List
import jwt
from datetime import datetime, timezone
from connexion.exceptions import OAuthProblem

SECRET_KEY = "secret-key"
ALGORITHM = "HS256"

from swagger_server.db import blacklist_collection


def check_BearerAuth(token):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        jti = payload.get("jti")
        if jti and blacklist_collection.find_one({"jti": jti}):
            raise OAuthProblem("Token has been revoked")
        
        # Check if token has expired (jwt.decode already checks this, but double-check)
        exp = payload.get("exp")
        if exp and datetime.fromtimestamp(exp, tz=timezone.utc) < datetime.now(timezone.utc):
            raise OAuthProblem("Token has expired")
        
        return {
            'user_id': payload.get('user_id'),
            'username': payload.get('username'),
            'role': payload.get('role'),
            'scopes': payload.get('scopes', []),
            'jti': jti,
            'exp': exp,
            'iat': payload.get('iat')
        }
        
    except jwt.ExpiredSignatureError:
        raise OAuthProblem("Token has expired")
        
    except jwt.InvalidTokenError as e:
        raise OAuthProblem(f"Invalid token: {str(e)}")
        
    except Exception as e:
        raise OAuthProblem(f"Token verification failed: {str(e)}")


