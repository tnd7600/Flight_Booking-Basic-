from sqlalchemy import (
    Column,
    String,
    Boolean,
    DateTime,
    Integer,
    Float,
    ForeignKey,
    CheckConstraint,
)
from sqlalchemy.orm import relationship
from database.database import Base


class Booking(Base):
    __tablename__ = "bookings"

    booking_id = Column(String(36), primary_key=True, nullable=False)
    flight_id = Column(String(36), ForeignKey("flights.flight_id"), nullable=True)
    flight_name = Column(String(255), nullable=True)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    email = Column(String(255), nullable=False)
    phone_no = Column(String(15), nullable=False)
    journey_date = Column(String, nullable=False, index=True)
    start_point = Column(String(100), nullable=False)
    end_point = Column(String(100), nullable=False)
    no_of_adults = Column(Integer, default=0)
    no_of_children = Column(Integer, default=0)
    no_of_infants = Column(Integer, default=0)
    journey_time = Column(String(5), default="na", nullable=False)
    bill_amount = Column(Float, default=0.0, nullable=False)
    booked_at = Column(DateTime, default=None, nullable=True)
    canceled_at = Column(DateTime, default=None, nullable=True)
    in_process = Column(Boolean, default=True, nullable=False)
    is_booked = Column(Boolean, default=False, nullable=False)
    is_canceled = Column(Boolean, default=False, nullable=False)

    flights = relationship("Flight", back_populates="bookings")
    users = relationship("User", back_populates="bookings")

    __table_args__ = (
        CheckConstraint("no_of_adults >= 0", name="check_no_of_adults_positive"),
        CheckConstraint("no_of_children >= 0", name="check_no_of_children_positive"),
        CheckConstraint("no_of_infants >= 0", name="check_no_of_infants_positive"),
    )


