import jwt
import datetime
from functools import wraps
from flask import session, jsonify, abort, request
import database.db as db
import secrets

SECRET_KEY = secrets.token_hex(32)
ALGORITHM = "HS256"

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            auth_header = request.headers.get("Authorization")
            token = auth_header.split(" ")[1]
        except:
            return {'message': "Unauthorised"}, 401

        if not token or not verify_jwt(token):
            return {'message': "Unauthorised"}, 401
        
        
        return f(*args, **kwargs)
    return decorated_function


def check_permissions(event_id):
    auth_header = request.headers.get("Authorization")
    token = verify_jwt(auth_header.split(" ")[1])
    
     
    user = db.get_user(token['username'])
    owner_id = db.get_event(event_id)
    
    if owner_id == None:
        return {'message': 'Event not found!'}
    owner_id = owner_id['owner_id']

    orgs = [i[0] for i in list(db.get_event_orgs(event_id))]


    if owner_id == None:
        return 404

    if user['id'] != owner_id and user['id'] not in orgs and user['role'] != 'admin':
        return 403

    return 200     


def create_jwt(payload: dict, expires_minutes: int = 60) -> str:
    payload_copy = payload.copy()
    payload_copy["exp"] = datetime.datetime.utcnow() + datetime.timedelta(minutes=expires_minutes)
    token = jwt.encode(payload_copy, SECRET_KEY, algorithm=ALGORITHM)
    return token


def verify_jwt(token: str) -> dict | None:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        print("Token expired")
        return None
    except jwt.InvalidTokenError:
        print("Invalid token")
        return None

