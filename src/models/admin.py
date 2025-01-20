from sqlalchemy import Column, String, Boolean, ForeignKey
from database.database import Base


class Admin(Base):
    __tablename__ = "Admins"

    id = Column(String(36), primary_key=True, nullable=False)
    name = Column(String(100), nullable=False)
    user_name = Column(String(50), nullable=False, unique=True)
    email = Column(String(255), nullable=False, unique=True)
    password = Column(String(255), nullable=False)
    post = Column(String(50), default="staff", nullable=False)
    key = Column(String(50), default="td", nullable=False)
    is_fired = Column(Boolean, default=False, nullable=False)
    is_resigned = Column(Boolean, default=False, nullable=False)
