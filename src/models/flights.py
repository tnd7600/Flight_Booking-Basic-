from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime
from sqlalchemy.orm import relationship
from database.database import Base


class Flight(Base):
    __tablename__ = "flights"

    flight_id = Column(
        String(36), primary_key=True, nullable=False, unique=True, index=True
    )
    flight_name = Column(String(255), nullable=False)
    start_point = Column(String(100), nullable=False)
    end_point = Column(String(100), nullable=False)
    journey_date = Column(String, nullable=False)
    journey_time = Column(String(5), nullable=False)
    available_capacity = Column(Integer, default=200, nullable=False)
    flight_price = Column(Float, default=15000.0, nullable=False)
    is_cancelled = Column(Boolean, default=False, nullable=False)

    bookings = relationship(
        "Booking", back_populates="flights", cascade="all, delete-orphan"
    )
