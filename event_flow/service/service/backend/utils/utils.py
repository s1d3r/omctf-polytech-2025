from datetime import datetime
import bcrypt
import hashlib

def make_invitecode(username, title):
    return hashlib.sha256(f"{str(username)}:{title}".encode('utf-8')).hexdigest()


def check_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
