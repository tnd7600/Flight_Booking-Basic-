from database.database import SessionLocal
from src.models.admin import Admin
from fastapi import HTTPException
from logs.log_config import logger

db = SessionLocal()

def find_same_user(field_name: str, value: str):
    user = db.query(Admin).filter(getattr(Admin, field_name) == value).first()
    if user:
        if user.is_fired == False and user.is_resigned == False:
            logger.error(f"{field_name.capitalize()} already exists")
            raise HTTPException(
                status_code=400, detail=f"{field_name.capitalize()} already exists"
            )
        if user.is_resigned == True:
            logger.error(
                f"{field_name.capitalize()} already exists but person resigned ago"
            )
            raise HTTPException(
                status_code=400,
                detail=f"{field_name.capitalize()} already exists but this person resigned ago",
            )
        if user.is_fired == True:
            logger.error(
                f"{field_name.capitalize()} already exists but person fired ago"
            )
            raise HTTPException(
                status_code=400,
                detail=f"{field_name.capitalize()} already exists but this person fired ago",
            )


from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def pass_checker(user_pass, hash_pass):
    if pwd_context.verify(user_pass, hash_pass):
        return True
    else:
        logger.error("Password is incorrect")
        raise HTTPException(status_code=401, detail="Password is incorrect")


from config import SECRET_KEY, ALGORITHM
from datetime import datetime, timedelta, timezone
import jwt
from fastapi import HTTPException, status


def get_token(id: str, post: str):

    payload = {
        "id": id,
        "post": post,
        "exp": datetime.now(timezone.utc) + timedelta(days=7),
    }

    access_token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return {"access_token": access_token}


def decode_token(token: str):
    try:

        payload = jwt.decode(token, SECRET_KEY, algorithms=ALGORITHM)
        id = payload.get("id")
        post = payload.get("post")

        if not id or not post:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Invalid token",
            )
        return id, post

    except jwt.ExpiredSignatureError:
        logger.error("Token has expired")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Token has expired",
        )

    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid token",
        )
