from functools import wraps
from flask import request, jsonify, current_app
import jwt
from api.auth.roles import has_permission

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({"error": "Token wymagany."}), 401

        try:
            token = token.replace("Bearer ", "")
            decoded = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=["HS256"])
            request.user = decoded  
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token wygasł."}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "Nieprawidłowy token."}), 401

        return f(*args, **kwargs)
    return decorated


def role_required(permission):
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            user = getattr(request, 'user', None)
            if not user:
                print("❌ Brak użytkownika w żądaniu.")
                return jsonify({"error": "Brak danych użytkownika."}), 401

            user_role = user.get("role", "user")
            print(f"🔎 Sprawdzanie uprawnień dla roli: {user_role}, wymagane: {permission}")  # DEBUG

            if not has_permission(user_role, permission):
                print("❌ Brak uprawnień.")
                return jsonify({"error": "Brak uprawnień."}), 403

            return f(*args, **kwargs)
        return decorated
    return decorator
