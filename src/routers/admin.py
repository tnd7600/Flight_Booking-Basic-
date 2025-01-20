from fastapi import APIRouter, HTTPException, Header
from database.database import SessionLocal
from src.schemas.admin import (
    Staff_Register_Schema,
    Admin_Register_Schema,
    Get_All_User_Schema,
)
from src.utils.admin import (
    pass_checker,
    find_same_user,
    get_token,
    decode_token,
    pwd_context,
)
from src.models.admin import Admin
from src.models.user import User
from logs.log_config import logger
import uuid

admin_router = APIRouter()
db = SessionLocal()


@admin_router.post("/register_admin")
def Register_Admin(staff: Admin_Register_Schema):
    logger.info("Registering new admin.")
    if staff.key != "td":
        logger.error("Admin registration failed due to incorrect key.")
        raise HTTPException(status_code=400, detail="Key Doesn't Match")

    new_staff = Admin(
        id=str(uuid.uuid4()),
        name=staff.name,
        user_name=staff.user_name,
        email=staff.email,
        password=pwd_context.hash(staff.password),
        post=staff.post,
        key=staff.key,
    )

    db.add(new_staff)
    db.commit()
    db.refresh(new_staff)

    logger.success(f"Admin {staff.name} registered successfully.")
    return "Admin Registered"


@admin_router.get("/staff_sign_in")
def Staff_Sign_In(email: str, password: str):
    logger.info(f"Login attempt for email: {email}")
    find_staff = db.query(Admin).filter(Admin.email == email).first()

    if not find_staff:
        logger.error("Invalid user during staff login.")
        raise HTTPException(status_code=400, detail="Invalid user")

    pass_checker(password, find_staff.password)
    access_token = get_token(find_staff.id, find_staff.post)

    logger.success(f"Login successful for user: {find_staff.name}")
    return "Login successful", access_token


@admin_router.post("/add_new_staff")
def Add_New_Staff(staff: Staff_Register_Schema, token: str = Header(...)):
    logger.info(f"Registering staff: {staff.name}")
    user_details = decode_token(token)
    id, post = user_details

    if post not in ["admin", "manager"]:
        logger.error("Access forbidden during staff registration.")
        raise HTTPException(status_code=400, detail="Access forbidden")

    find_same_user("email", staff.email)
    find_same_user("user_name", staff.user_name)

    new_staff = Admin(
        id=str(uuid.uuid4()),
        name=staff.name,
        user_name=staff.user_name,
        email=staff.email,
        password=pwd_context.hash(staff.password),
        post=staff.post,
    )

    db.add(new_staff)
    db.commit()
    db.refresh(new_staff)

    logger.success(f"Staff {staff.name} registered successfully.")
    return "Staff Registered Successfully"


@admin_router.get("/get_all_users_data", response_model=list[Get_All_User_Schema])
def Get_All_Users_Data(token: str = Header(...)):
    logger.info("Fetching all active users.")
    user_details = decode_token(token)
    id, post = user_details

    if post != "admin":
        logger.error("Access forbidden during fetching users.")
        raise HTTPException(status_code=400, detail="Access forbidden")

    all_users = (
        db.query(User)
        .filter(
            User.is_active == True, User.is_deleted == False, User.is_verified == True
        )
        .all()
    )
    if not all_users:
        logger.error("No users found.")
        raise HTTPException(status_code=400, detail="No Users Found")

    logger.success("Active users data retrieved successfully.")
    return all_users


@admin_router.get(
    "/get_single_user_data/{user_email}", response_model=Get_All_User_Schema
)
def Get_Single_User_Data(user_email: str, token: str = Header(...)):
    logger.info(f"Fetching user data for email: {user_email}.")
    user_details = decode_token(token)
    id, post = user_details

    if post not in ["admin", "manager"]:
        logger.error("Access forbidden during fetching user data.")
        raise HTTPException(status_code=400, detail="Access forbidden")

    find_user = (
        db.query(User)
        .filter(
            User.email == user_email,
            User.is_active == True,
            User.is_deleted == False,
            User.is_verified == True,
        )
        .first()
    )

    if not find_user:
        logger.error(f"No user found with email: {user_email}.")
        raise HTTPException(status_code=400, detail="User Not Found")

    logger.success(f"User data for {user_email} retrieved successfully.")
    return find_user
