from fastapi import HTTPException, status
from database.database import SessionLocal
from src.models.flights import Flight
from config import SECRET_KEY, ALGORITHM
import jwt
from logs.log_config import logger

db = SessionLocal()


def search_for_copy(flight_name: str, date: str, time: str):
    logger.info(f"Checking for duplicate flight: {flight_name} on {date} at {time}.")
    copy_flight = (
        db.query(Flight)
        .filter(
            Flight.flight_name == flight_name,
            Flight.journey_date == date,
            Flight.journey_time == time,
        )
        .first()
    )

    if copy_flight:
        logger.warning(f"Duplicate flight found: {flight_name} on {date} at {time}.")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Flight already exists"
        )

    logger.info(f"No duplicate flight found for {flight_name} on {date} at {time}.")


def decode_token(token: str):
    logger.info("Decoding token.")
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        id = payload.get("id")
        post = payload.get("post")

        if not id or not post:
            logger.error("Token decoding failed. Missing 'id' or 'post'.")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Invalid token",
            )

        logger.debug(f"Token decoded successfully for user ID: {id}, Role: {post}.")
        return id, post

    except jwt.ExpiredSignatureError:
        logger.error("Token has expired.")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Token has expired",
        )

    except jwt.InvalidTokenError:
        logger.error("Invalid token provided.")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid token",
        )
