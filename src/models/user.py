from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from database.database import Base
from datetime import datetime


class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, nullable=False)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    password = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False)
    phone_no = Column(String(15), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    is_created = Column(DateTime, default=datetime.now, nullable=False)
    is_modified = Column(
        DateTime, default=datetime.now, onupdate=datetime.now, nullable=False
    )
    is_deleted = Column(Boolean, default=False, nullable=False)

    bookings = relationship("Booking", back_populates="users")


class OTP(Base):
    __tablename__ = "otps"

    id = Column(String(36), primary_key=True, nullable=False)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    email = Column(String(255), nullable=False)
    otp = Column(String(6), nullable=False)
