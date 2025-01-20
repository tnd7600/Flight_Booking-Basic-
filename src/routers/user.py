from fastapi import APIRouter, HTTPException, Header
from database.database import SessionLocal
from src.schemas.user import (
    Update_User_Schema,
    Register_User_Schema,
    Reset_pass_Schema,
    Forget_pass_Schema,
)
from src.models.user import User
from src.utils.user import (
    find_same_email,
    pwd_context,
    get_token,
    decode_token,
    pass_checker,
    generate_otp,
    verify_otp,
)
from logs.log_config import logger
import uuid


user_router = APIRouter()
db = SessionLocal()


@user_router.post("/sign_up")
def Sign_Up(user: Register_User_Schema):
    logger.info("Starting user registration process.")
    new_user = User(
        id=str(uuid.uuid4()),
        first_name=user.first_name,
        last_name=user.last_name,
        email=user.email,
        password=pwd_context.hash(user.password),
        phone_no=user.phone_no,
    )

    logger.info("Checking for existing users.")
    find_minimum_one_entry = db.query(User).first()
    if find_minimum_one_entry:
        find_same_email(user.email)

    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    logger.success(f"User registered successfully. User ID: {new_user.id}")

    return {
        "message": "User registered successfully. Please proceed with verification."
    }


@user_router.post("/generate_otp")
def Generate_OTP(email: str):
    logger.info(f"Generating OTP for email: {email}.")
    generate_otp(email)
    logger.success(f"OTP generated and sent to {email}.")
    return {"message": "OTP generated successfully."}


@user_router.get("/verify_otp")
def Verify_OTP(email: str, otp: str):
    logger.info(f"Verifying OTP for email: {email}.")
    find_user = (
        db.query(User)
        .filter(
            User.email == email,
            User.is_active == True,
            User.is_verified == False,
            User.is_deleted == False,
        )
        .first()
    )

    if not find_user:
        logger.error(f"User not found or already verified. Email: {email}")
        raise HTTPException(
            status_code=400, detail="User not found or already verified."
        )

    verify_otp(email, otp)
    find_user.is_verified = True
    db.commit()
    db.refresh(find_user)
    logger.success(f"OTP verified for email: {email}. User is now verified.")
    return {"message": "OTP verified successfully."}


@user_router.get("/sign_in")
def Sign_In(email: str, password: str):
    logger.info(f"Attempting login for email: {email}.")
    find_user = (
        db.query(User)
        .filter(
            User.email == email,
            User.is_active == True,
            User.is_verified == True,
            User.is_deleted == False,
        )
        .first()
    )

    if not find_user:
        logger.error(f"Login failed. User not found. Email: {email}")
        raise HTTPException(status_code=400, detail="User not found")

    logger.info(f"Verifying password for email: {email}.")
    pass_checker(password, find_user.password)

    access_token = get_token(
        find_user.id,
        find_user.first_name,
        find_user.last_name,
        find_user.email,
        find_user.phone_no,
    )
    logger.success(f"User login successful. Email: {email}")
    return {"message": "Login successful.", "access_token": access_token}


@user_router.patch("/update_details")
def Update_Details(user: Update_User_Schema, token: str = Header(...)):
    user_details = decode_token(token)
    id, first_name, last_name, email, phone_no = user_details
    logger.info(f"Updating user details for id: {id}.")

    find_user = (
        db.query(User)
        .filter(
            User.id == id,
            User.is_active == True,
            User.is_verified == True,
            User.is_deleted == False,
        )
        .first()
    )

    if not find_user:
        logger.error(f"User not found for update. id: {id}")
        raise HTTPException(status_code=400, detail="User not found")

    new_user_schema_without_none = user.model_dump(exclude_none=True)

    for key, value in new_user_schema_without_none.items():
        if key == "password":
            setattr(find_user, key, pwd_context.hash(value))
        else:
            find_same_email(value)
            setattr(find_user, key, value)
    db.commit()
    db.refresh(find_user)
    access_token = get_token(
        find_user.id,
        find_user.first_name,
        find_user.last_name,
        find_user.email,
        find_user.phone_no,
    )
    logger.success(f"User details updated successfully. id: {id}")
    return {
        "message": "User updated successfully.",
        "user": find_user,
        "access_token": access_token,
    }


@user_router.delete("/delete_account")
def Delete_Account(password: str, token: str = Header(...)):
    user_details = decode_token(token)
    id, first_name, last_name, email, phone_no = user_details
    logger.info(f"Deleting account for id: {id}.")

    find_user = (
        db.query(User)
        .filter(User.id == id, User.is_active == True, User.is_verified == True)
        .first()
    )

    if not find_user:
        logger.error(f"User not found for deletion. id: {id}")
        raise HTTPException(status_code=400, detail="User not found")

    pass_checker(password, find_user.password)

    if find_user.is_deleted:
        logger.error(f"Attempt to delete an already deleted account. id: {id}")
        raise HTTPException(status_code=400, detail="User already deleted")

    find_user.is_deleted = True
    find_user.is_active = False
    find_user.is_verified = False

    db.commit()
    db.refresh(find_user)
    logger.success(f"Account deleted successfully. id: {id}")
    return {"message": "User deleted successfully.", "user": find_user}


@user_router.put("/reset_password")
def Reset_Password(user: Reset_pass_Schema, token: str = Header(...)):
    user_details = decode_token(token)
    id, first_name, last_name, email, phone_no = user_details
    logger.info(f"Resetting password for email: {id}.")

    find_user = (
        db.query(User)
        .filter(
            User.id == id,
            User.is_active == True,
            User.is_verified == True,
            User.is_deleted == False,
        )
        .first()
    )

    if not find_user:
        logger.error(f"User not found for password reset. id: {id}")
        raise HTTPException(status_code=400, detail="User not found")

    pass_checker(user.enter_old_password, find_user.password)

    if user.enter_new_password == user.re_enter_new_password:
        find_user.password = pwd_context.hash(user.enter_new_password)
    else:
        logger.error(f"Password mismatch during reset. id: {id}")
        raise HTTPException(status_code=400, detail="Passwords do not match")

    db.commit()
    db.refresh(find_user)
    logger.success(f"Password reset successfully. id: {id}")
    return {"message": "Password reset successfully."}


@user_router.post("/forget_password_generate_otp")
def Forget_Password_Generate_OTP(email: str):
    logger.info(f"Generating OTP for password recovery. Email: {email}.")
    generate_otp(email)
    logger.success(f"OTP generated for password recovery. Email: {email}.")
    return {"message": "OTP generated successfully."}


@user_router.put("/forget_password")
def Forget_Password(user: Forget_pass_Schema):
    logger.info(f"Handling forget password for email: {user.user_email}.")
    find_user = (
        db.query(User)
        .filter(
            User.email == user.user_email,
            User.is_active == True,
            User.is_verified == True,
            User.is_deleted == False,
        )
        .first()
    )

    if not find_user:
        logger.error(f"User not found for forget password. Email: {user.user_email}")
        raise HTTPException(status_code=400, detail="User not found")

    verify_otp(user.user_email, user.otp)
    find_user.password = pwd_context.hash(user.enter_new_password)

    db.commit()
    db.refresh(find_user)
    logger.success(f"Password changed successfully. Email: {user.user_email}")
    return {"message": "Password changed successfully."}
