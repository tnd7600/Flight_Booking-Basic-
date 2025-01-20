from fastapi import APIRouter, HTTPException, Header
from database.database import SessionLocal
from src.schemas.flights import (
    Register_Flight_Schema,
    Find_Flight_Schema,
    Update_Flight_Schema,
    All_Flight_Schema,
)
from src.utils.flights import search_for_copy, decode_token
from src.models.flights import Flight
from logs.log_config import logger
import uuid


flight_router = APIRouter()
db = SessionLocal()


@flight_router.post("/register_new_flight")
def Register_New_Flight(flight: Register_Flight_Schema, token: str = Header(...)):
    logger.info("Register flight request received.")
    user_details = decode_token(token)
    id, post = user_details

    logger.debug(f"Decoded token for user ID: {id}, Role: {post}")
    if post not in ["admin", "manager"]:
        logger.warning(f"Access forbidden for user ID: {id}, Role: {post}")
        raise HTTPException(status_code=403, detail="Access forbidden")

    search_for_copy(flight.flight_name, flight.journey_date, flight.journey_time)
    logger.debug(
        f"No duplicate flight found for {flight.flight_name} on {flight.journey_date} at {flight.journey_time}"
    )

    new_flight = Flight(
        flight_id=str(uuid.uuid4()),
        flight_name=flight.flight_name,
        journey_date=flight.journey_date,
        journey_time=flight.journey_time,
        start_point=flight.start_point,
        end_point=flight.end_point,
        available_capacity=flight.available_capacity,
        flight_price=flight.flight_price,
    )

    db.add(new_flight)
    db.commit()

    logger.info(
        f"Flight registered successfully: {new_flight.flight_name}, ID: {new_flight.flight_id}"
    )
    return {"message": "Flight details added successfully"}


@flight_router.put("/update_flight_details")
def Update_Flight_Details(flight: Update_Flight_Schema, token: str = Header(...)):
    logger.info("Flight update request received.")
    user_details = decode_token(token)
    id, post = user_details

    logger.debug(f"Decoded token for user ID: {id}, Role: {post}")
    if post not in ["admin", "manager"]:
        logger.warning(f"Access forbidden for user ID: {id}, Role: {post}")
        raise HTTPException(status_code=403, detail="Access forbidden")

    old_flight = (
        db.query(Flight)
        .filter(
            Flight.flight_name == flight.flight_name,
            Flight.journey_date == flight.journey_date,
            Flight.journey_time == flight.journey_time,
        )
        .first()
    )

    if not old_flight:
        logger.error(
            f"Flight not found: {flight.flight_name} on {flight.journey_date} at {flight.journey_time}"
        )
        raise HTTPException(status_code=404, detail="Flight not found")

    search_for_copy(flight.new_flight_name, flight.new_date, flight.new_time)
    logger.debug(
        f"Duplicate check passed for new flight details: {flight.new_flight_name}, {flight.new_date}, {flight.new_time}"
    )

    old_flight.flight_name = flight.new_flight_name
    old_flight.journey_time = flight.new_time
    old_flight.journey_date = flight.new_date
    old_flight.start_point = flight.start_point
    old_flight.end_point = flight.end_point
    old_flight.available_capacity = flight.available_capacity
    old_flight.flight_price = flight.flight_price

    db.commit()

    logger.info(
        f"Flight updated successfully: {old_flight.flight_name}, ID: {old_flight.flight_id}"
    )
    return {"message": "Flight details updated successfully"}


@flight_router.post("/cancel_flight")
def Cancel_Flight(flight: Find_Flight_Schema, token: str = Header(...)):
    logger.info("Flight cancellation request received.")
    user_details = decode_token(token)
    id, post = user_details

    logger.debug(f"Decoded token for user ID: {id}, Role: {post}")
    if post not in ["admin", "manager"]:
        logger.warning(f"Access forbidden for user ID: {id}, Role: {post}")
        raise HTTPException(status_code=403, detail="Access forbidden")

    old_flight = (
        db.query(Flight)
        .filter(
            Flight.flight_name == flight.flight_name,
            Flight.journey_date == flight.journey_date,
            Flight.journey_time == flight.journey_time,
        )
        .first()
    )

    if not old_flight:
        logger.error(
            f"Flight not found: {flight.flight_name} on {flight.journey_date} at {flight.journey_time}"
        )
        raise HTTPException(status_code=404, detail="Flight not found")

    old_flight.is_cancelled = True
    db.commit()

    logger.info(
        f"Flight cancelled successfully: {old_flight.flight_name}, ID: {old_flight.flight_id}"
    )
    return {"message": "Flight cancelled successfully"}


@flight_router.get("/get_all_flight_details", response_model=list[All_Flight_Schema])
def Get_All_Flight_Details(token: str = Header(...)):
    logger.info("Fetching all flight data request received.")
    user_details = decode_token(token)
    id, post = user_details

    logger.debug(f"Decoded token for user ID: {id}, Role: {post}")
    if post != "admin":
        logger.warning(f"Access forbidden for user ID: {id}, Role: {post}")
        raise HTTPException(status_code=403, detail="Access forbidden")

    all_flights = db.query(Flight).all()

    if not all_flights:
        logger.warning("No flight data available")
        raise HTTPException(status_code=404, detail="No flight data available")

    logger.info("Successfully fetched all flight data.")
    return all_flights
