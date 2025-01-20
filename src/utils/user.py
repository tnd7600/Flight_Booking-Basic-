from database.database import SessionLocal
from src.models.user import User, OTP
from fastapi import HTTPException
from logs.log_config import logger
from passlib.context import CryptContext
from config import SECRET_KEY, ALGORITHM
from datetime import datetime, timedelta, timezone
import jwt
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from config import SENDER_EMAIL_ID, EMAIL_PASSKEY
import random, uuid


db = SessionLocal()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def find_same_email(email: str):
    try:
        find_same_email = db.query(User).filter(User.email == email).first()
        logger.info(f"Verifying email: {email}")

        if find_same_email:
            if find_same_email.is_active == True:
                logger.error(f"Email {email} already exists.")
                raise HTTPException(status_code=400, detail="Email already exists")
            if find_same_email.is_active == False:
                logger.error(f"Email {email} exists but the account is deleted.")
                raise HTTPException(
                    status_code=400,
                    detail="Email already exists but this account is deleted. Try with a different email",
                )
    except Exception as e:
        logger.error(f"Error in find_same_email: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")


def pass_checker(user_pass: str, hash_pass: str):
    try:
        if pwd_context.verify(user_pass, hash_pass):
            return True
        else:
            logger.error("Password is incorrect")
            raise HTTPException(status_code=401, detail="Password is incorrect")
    except Exception as e:
        logger.error(f"Error in pass_checker: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")


def get_token(id: str, first_name: str, last_name: str, email: str, phone_no: str):
    try:
        payload = {
            "id": id,
            "first_name": first_name,
            "last_name": last_name,
            "email": email,
            "phone_no": phone_no,
            "exp": datetime.now(timezone.utc) + timedelta(days=7),
        }
        access_token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
        logger.info(f"Token generated for user {email}")
        return {"access_token": access_token}
    except Exception as e:
        logger.error(f"Error in get_token: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")


def decode_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=ALGORITHM)
        id = payload.get("id")
        first_name = payload.get("first_name")
        last_name = payload.get("last_name")
        email = payload.get("email")
        phone_no = payload.get("phone_no")

        if not id or not first_name or not last_name or not email or not phone_no:
            logger.error("Invalid token")
            raise HTTPException(status_code=403, detail="Invalid token")
        logger.info("Token decoded successfully")
        return id, first_name, last_name, email, phone_no

    except jwt.ExpiredSignatureError:
        logger.error("Token has expired")
        raise HTTPException(status_code=403, detail="Token has expired")
    except jwt.InvalidTokenError as e:
        logger.error(f"Invalid token: {e}")
        raise HTTPException(status_code=403, detail="Invalid token")


def send_email(receiver: str, subject: str, body: str):
    try:
        smtp_server = "smtp.gmail.com"
        smtp_port = 587
        smtp_user = SENDER_EMAIL_ID
        smtp_pass = EMAIL_PASSKEY

        msg = MIMEMultipart()
        msg["From"] = SENDER_EMAIL_ID
        msg["To"] = receiver
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))

        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.set_debuglevel(1)
            server.starttls()
            server.login(smtp_user, smtp_pass)
            server.sendmail(SENDER_EMAIL_ID, receiver, msg.as_string())
        logger.info(f"OTP email sent to {receiver}")
        return True
    except Exception as e:
        logger.error(f"Error in send_email: {e}")
        raise HTTPException(status_code=500, detail="Failed to send OTP email")


def generate_otp(email: str):
    try:
        logger.info(f"Getting user data for email: {email}")
        find_user = (
            db.query(User)
            .filter(
                User.email == email, User.is_active == True, User.is_deleted == False
            )
            .first()
        )

        if not find_user:
            logger.error(f"User not found with email: {email}")
            raise HTTPException(status_code=400, detail="User not found")

        logger.info(f"Generating OTP for {email}")
        random_otp = random.randint(1000, 9999)

        new_otp = OTP(
            id=str(uuid.uuid4()),
            user_id=find_user.id,
            email=find_user.email,
            otp=random_otp,
        )

        logger.info(f"Sending OTP email to {email}")
        send_email(find_user.email, "Send OTP", f"OTP is {random_otp}")

        db.add(new_otp)
        db.commit()
        db.refresh(new_otp)
        logger.success(f"Verification OTP sent successfully to {email}")
    except Exception as e:
        logger.error(f"Error in generate_otp: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")


def verify_otp(email: str, otp: str):
    try:
        logger.info(f"Verifying OTP for email: {email}")
        find_otp = db.query(OTP).filter(OTP.email == email, OTP.otp == otp).first()

        if not find_otp:
            logger.error(f"Wrong OTP entered for email: {email}")
            raise HTTPException(status_code=400, detail="OTP not found")

        logger.info("OTP verified successfully")
        db.delete(find_otp)
        db.commit()
    except Exception as e:
        logger.error(f"Error in verify_otp: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
