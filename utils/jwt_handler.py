import jwt
import datetime

SECRET = "supersecret"  # Replace with env variable later

def create_token(data: dict):
    payload = {
        **data,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=12)
    }
    return jwt.encode(payload, SECRET, algorithm="HS256")
