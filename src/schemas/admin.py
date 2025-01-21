from pydantic import BaseModel, EmailStr, Field
from typing import Optional


class Staff_Register_Schema(BaseModel):
    name: str = Field(..., description="Name of the staff member.")
    user_name: str = Field(..., description="Unique username for the staff member.")
    email: EmailStr = Field(..., description="Email address of the staff member.")
    password: str = Field(
        ..., description="Password for the staff member (min. 8 characters)."
    )
    post: str = Field(..., description="Position or post held by the staff member.")

    class Config:
        json_schema_extra = {
            "example": {
                "name": "John Doe",
                "user_name": "john_doe",
                "email": "john.doe@example.com",
                "password": "password123",
                "post": "Manager",
            }
        }
 


class Admin_Register_Schema(BaseModel):
    name: str = Field(..., description="Name of the admin.")
    user_name: str = Field(..., description="Unique username for the admin.")
    email: EmailStr = Field(..., description="Email address of the admin.")
    password: str = Field(
        ..., description="Password for the admin (min. 8 characters)."
    )
    post: str = Field(..., description="Position or post held by the admin.")
    key: str = Field(..., description="Unique key for admin verification.")

    class Config:
        json_schema_extra = {
            "example": {
                "name": "Admin Name",
                "user_name": "admin_name",
                "email": "admin.name@example.com",
                "password": "adminpassword123",
                "post": "Administrator",
                "key": "unique_admin_key",
            }
        }

 

class Get_All_User_Schema(BaseModel):
    id: str = Field(..., description="Unique identifier of the user.")
    first_name: str = Field(..., description="First name of the user.")
    last_name: str = Field(..., description="Last name of the user.")
    email: EmailStr = Field(..., description="Email address of the user.")

    class Config:
        json_schema_extra = {
            "example": {
                "id": "123",
                "first_name": "John",
                "last_name": "Doe",
                "email": "john.doe@example.com",
            }
        }



class Update_Staff_Schema(BaseModel):
    name: Optional[str] = None
    user_name: Optional[str] = None
    email: Optional[EmailStr] = None

