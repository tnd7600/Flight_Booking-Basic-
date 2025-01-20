from fastapi import APIRouter, HTTPException, Header
from database.database import SessionLocal
from src.schemas.booking import (
    Date_Route_Passengers_Select_Schema,
    Available_Flight_Schema,
)
from src.utils.booking import decode_token, generate_otp, verify_otp
from src.models.user import User
from src.models.booking import Booking
from src.models.flights import Flight
from logs.log_config import logger
import uuid
from datetime import datetime

booking_router = APIRouter()
db = SessionLocal()



@booking_router.post("/select_date_route_passengers")
def Select_Date_Route_Passengers(
    details: Date_Route_Passengers_Select_Schema, token: str = Header(...)
):
    logger.info("Starting the booking process for a user.")
    user_details = decode_token(token)
    id, first_name, last_name, email, phone_no = user_details

    new_booking = Booking(
        booking_id=str(uuid.uuid4()),
        user_id=id,
        first_name=first_name,
        last_name=last_name,
        email=email,
        phone_no=phone_no,
        journey_date=details.journey_date,
        start_point=details.start_point,
        end_point=details.end_point,
        no_of_adults=details.no_of_adults,
        no_of_children=details.no_of_children,
        no_of_infants=details.no_of_infants,
    )

    db.add(new_booking)
    db.commit()
    db.refresh(new_booking)

    logger.success(f"Booking details saved with ID: {new_booking.booking_id}")
    return {"message": "Booking details saved", "booking_id": new_booking.booking_id}




@booking_router.get(
    "/get_available_flights", response_model=list[Available_Flight_Schema]
)
def Get_Available_Flights(booking_id: str):
    logger.info(f"Fetching available flights for booking ID: {booking_id}")
    find_booking = db.query(Booking).filter(Booking.booking_id == booking_id).first()

    if not find_booking:
        logger.error(f"No booking found for ID: {booking_id}")
        raise HTTPException(status_code=404, detail="Booking not found")

    find_flights = (
        db.query(Flight)
        .filter(
            Flight.journey_date == find_booking.journey_date,
            Flight.start_point == find_booking.start_point,
            Flight.end_point == find_booking.end_point,
            Flight.available_capacity
            >= find_booking.no_of_adults + find_booking.no_of_children,
        )
        .all()
    )

    if not find_flights:
        logger.warning(f"No flights available for criteria: {find_booking}")
        raise HTTPException(status_code=400, detail="No flights available")

    logger.success(f"Found {len(find_flights)} flights for booking ID: {booking_id}")
    return find_flights



@booking_router.post("/select_time")
def Select_Time(booking_id: str, journey_time: str):
    logger.info(f"Selecting journey time for booking ID: {booking_id}")
    find_booking = db.query(Booking).filter(Booking.booking_id == booking_id).first()

    if not find_booking:
        logger.error(f"No booking found for ID: {booking_id}")
        raise HTTPException(status_code=404, detail="Booking not found")

    find_flight = (
        db.query(Flight)
        .filter(
            Flight.journey_date == find_booking.journey_date,
            Flight.start_point == find_booking.start_point,
            Flight.end_point == find_booking.end_point,
            Flight.journey_time == journey_time,
        )
        .first()
    )

    if not find_flight:
        logger.error(
            f"No flight available at time: {journey_time} for booking ID: {booking_id}"
        )
        raise HTTPException(
            status_code=400, detail="Flight not available at the selected time"
        )

    find_booking.journey_time = journey_time
    find_booking.flight_id = find_flight.flight_id
    find_booking.flight_name = find_flight.flight_name

    db.commit()
    db.refresh(find_booking)
    logger.success(
        f"Journey time selected for booking ID: {booking_id}, flight ID: {find_flight.flight_id}"
    )
    return {"message": "Time selected", "flight_id": find_flight.flight_id}



@booking_router.post("/send_payment_otp")
def Send_Payment_Otp(booking_id: str):
    logger.info(f"Initiating payment process for booking ID: {booking_id}")
    find_booking = db.query(Booking).filter(Booking.booking_id == booking_id).first()

    if not find_booking:
        logger.error(f"No booking found for ID: {booking_id}")
        raise HTTPException(status_code=404, detail="Booking not found")

    find_flight = (
        db.query(Flight).filter(Flight.flight_id == find_booking.flight_id).first()
    )

    bill_amount = (
        find_booking.no_of_adults + find_booking.no_of_children
    ) * find_flight.flight_price

    if find_booking.no_of_infants > 0:
        bill_amount += find_booking.no_of_infants * 5000

    find_booking.bill_amount = bill_amount
    generate_otp(find_booking.email, bill_amount)

    db.commit()
    db.refresh(find_booking)
    logger.success(
        f"OTP sent to email {find_booking.email} for payment of {bill_amount}"
    )
    return {"message": "OTP sent for payment confirmation"}



@booking_router.post("/verify_payment")
def Verify_Payment(booking_id: str, email: str, otp: str):
    logger.info(f"Verifying payment for booking ID: {booking_id}")
    find_booking = db.query(Booking).filter(Booking.booking_id == booking_id).first()

    if not find_booking:
        logger.error(f"No booking found for ID: {booking_id}")
        raise HTTPException(status_code=404, detail="Booking not found")

    verify_otp(email, otp)

    find_flight = (
        db.query(Flight).filter(Flight.flight_id == find_booking.flight_id).first()
    )
    find_booking.is_booked = True
    find_booking.in_process = False
    find_booking.booked_at = datetime.now()
    find_flight.available_capacity -= (
        find_booking.no_of_adults + find_booking.no_of_children
    )

    db.commit()
    db.refresh(find_booking)
    logger.success(f"Payment verified, booking completed for ID: {booking_id}")
    return {"message": "Payment verified, booking completed"}

 

@booking_router.post("/cancel_flight_booking")
def Cancel_Flight_Booking(booking_id: str):
    logger.info(f"Canceling booking with ID: {booking_id}")
    find_booking = db.query(Booking).filter(Booking.booking_id == booking_id).first()

    if not find_booking:
        logger.error(f"No booking found for ID: {booking_id}")
        raise HTTPException(status_code=404, detail="Booking not found")

    if not find_booking.is_booked:
        logger.warning(
            f"Attempt to cancel an unconfirmed booking with ID: {booking_id}"
        )
        raise HTTPException(
            status_code=400, detail="Cannot cancel an unconfirmed booking"
        )

    find_flight = (
        db.query(Flight).filter(Flight.flight_id == find_booking.flight_id).first()
    )

    find_booking.is_canceled = True
    find_booking.canceled_at = datetime.now()
    find_flight.available_capacity += (
        find_booking.no_of_adults + find_booking.no_of_children
    )

    db.commit()
    db.refresh(find_booking)
    logger.success(f"Booking {booking_id} canceled successfully")
    return {"message": "Booking canceled successfully", "booking_id": booking_id}
