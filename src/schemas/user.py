from pydantic import BaseModel, EmailStr, Field
from typing import Optional


class Register_User_Schema(BaseModel):
    first_name: str = Field(..., description="Enter your first name.")
    last_name: str = Field(..., description="Enter your last name.")
    password: str = Field(
        ..., description="Password must be at least 8 characters long."
    )
    email: EmailStr
    phone_no: str = Field(
        ...,
        pattern=r"^\+?[1-9]\d{1,14}$",
        description="Phone number must be a valid format.",
    )

    class Config:
        json_schema_extra = {
            "example": {
                "first_name": "John",
                "last_name": "Doe",
                "password": "StrongPassword123",
                "email": "johndoe@example.com",
                "phone_no": "+1234567890",
            }
        }



class Update_User_Schema(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "first_name": "John",
                "last_name": "Smith",
                "email": "johnsmith@example.com",
                "password": "NewPassword123",
            }
        }



class Reset_pass_Schema(BaseModel):
    enter_old_password: str = Field(
        ..., description="Old password should be at least 8 characters."
    )
    enter_new_password: str = Field(
        ..., description="New password should be at least 8 characters."
    )
    re_enter_new_password: str = Field(
        ..., description="New password confirmation should match the new password."
    )

    class Config:
        json_schema_extra = {
            "example": {
                "enter_old_password": "OldPassword123",
                "enter_new_password": "NewPassword456",
                "re_enter_new_password": "NewPassword456",
            }
        }



class Forget_pass_Schema(BaseModel):
    user_email: EmailStr
    otp: str = Field(..., description="OTP should be exactly 6 characters.")
    enter_new_password: str = Field(
        ..., description="New password should be at least 8 characters."
    )
    re_enter_new_password: str = Field(
        ..., description="New password confirmation should match the new password."
    )

    class Config:
        json_schema_extra = {
            "example": {
                "user_email": "johndoe@example.com",
                "otp": "1234",
                "enter_new_password": "NewPassword123",
                "re_enter_new_password": "NewPassword123",
            }
        }