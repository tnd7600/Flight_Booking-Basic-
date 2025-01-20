from logs.log_config import logger
from database.database import SessionLocal
from src.models.user import User, OTP
from fastapi import HTTPException, status
from config import SECRET_KEY, ALGORITHM, SENDER_EMAIL_ID, EMAIL_PASSKEY
import jwt
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import random
import uuid

db = SessionLocal()


def decode_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        id = payload.get("id")
        first_name = payload.get("first_name")
        last_name = payload.get("last_name")
        email = payload.get("email")
        phone_no = payload.get("phone_no")

        if not id or not first_name or not last_name or not email or not phone_no:
            logger.error("Invalid token payload.")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Invalid token",
            )
        return id, first_name, last_name, email, phone_no
    except jwt.ExpiredSignatureError:
        logger.error("Token has expired.")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Token has expired",
        )
    except jwt.InvalidTokenError:
        logger.error("Invalid token.")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid token",
        )


def send_email(receiver, subject, body):
    smtp_server = "smtp.gmail.com"
    smtp_port = 587
    smtp_user = SENDER_EMAIL_ID
    smtp_pass = EMAIL_PASSKEY

    msg = MIMEMultipart()
    msg["From"] = SENDER_EMAIL_ID
    msg["To"] = receiver
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.set_debuglevel(0)
            server.starttls()
            server.login(smtp_user, smtp_pass)
            server.sendmail(SENDER_EMAIL_ID, receiver, msg.as_string())
        logger.info(f"Email sent successfully to {receiver}")
        return True
    except Exception as e:
        logger.error(f"Failed to send email to {receiver}: {e}")
        raise HTTPException(status_code=500, detail="Failed to send email")


def generate_otp(email: str, bill_amount: str):
    logger.info(f"Attempting to generate OTP for email: {email}")
    find_user = db.query(User).filter(User.email == email).first()

    if not find_user:
        logger.error(f"No user found with email: {email}")
        raise HTTPException(status_code=404, detail="User not found")

    if bill_amount <= 0:
        logger.error(f"Invalid bill amount: {bill_amount}")
        raise HTTPException(status_code=400, detail="Invalid bill amount")

    logger.info("Generating OTP")
    random_otp = random.randint(1000, 9999)

    try:
        send_email(
            find_user.email,
            "Payment OTP",
            f"Your bill amount is {bill_amount}. OTP: {random_otp}",
        )
    except HTTPException as e:
        logger.error(f"Failed to send OTP email: {str(e)}")
        raise

    new_otp = OTP(
        id=str(uuid.uuid4()),
        user_id=find_user.id,
        email=find_user.email,
        otp=random_otp,
    )

    db.add(new_otp)
    db.commit()
    logger.success(f"OTP successfully generated and sent to {email}")


def verify_otp(email: str, otp: str):
    logger.info(f"Verifying OTP for email: {email}")
    find_otp = db.query(OTP).filter(OTP.email == email, OTP.otp == otp).first()

    if not find_otp:
        logger.error(f"Invalid OTP entered for email: {email}")
        raise HTTPException(status_code=400, detail="Invalid or expired OTP")

    logger.info(f"OTP verified for email: {email}")
    db.delete(find_otp)
    db.commit()
    logger.success(f"OTP for email {email} has been verified and deleted.")
