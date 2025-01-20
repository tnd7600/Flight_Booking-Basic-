from pydantic import BaseModel, Field


class Register_Flight_Schema(BaseModel):
    flight_name: str = Field(..., description="Name of the flight")
    journey_date: str = Field(..., description="Journey date in YYYY-MM-DD format")
    journey_time: str = Field(..., description="Journey time in HH:MM format")
    start_point: str = Field(..., description="Name of the Pickup Point")
    end_point: str = Field(..., description="Name of the Drop Point")
    available_capacity: int = Field(
        ...,
        ge=0,
        description="Available seat capacity of the flight (must be non-negative)",
    )
    flight_price: float = Field(
        ..., ge=0, description="Price of the flight per seat (must be non-negative)"
    )



class All_Flight_Schema(BaseModel):
    flight_name: str = Field(..., description="Name of the flight")
    journey_date: str = Field(..., description="Journey date in YYYY-MM-DD format")
    journey_time: str = Field(..., description="Journey time in HH:MM format")
    available_capacity: int = Field(
        ..., description="Available seat capacity of the flight"
    )



class Update_Flight_Schema(BaseModel):
    flight_name: str = Field(..., description="Current name of the flight")
    journey_date: str = Field(
        ..., description="Current journey date in YYYY-MM-DD format"
    )
    journey_time: str = Field(..., description="Current journey time in HH:MM format")
    new_flight_name: str = Field(..., description="New name of the flight")
    new_date: str = Field(..., description="New journey date in YYYY-MM-DD format")
    new_time: str = Field(..., description="New journey time in HH:MM format")
    start_point: str = Field(..., description="Updated name of the Pickup Point")
    end_point: str = Field(..., description="Updated name of the Drop Point")
    available_capacity: int = Field(
        ...,
        ge=0,
        description="Updated available seat capacity of the flight (must be non-negative)",
    )
    flight_price: float = Field(
        ...,
        ge=0,
        description="Updated price of the flight per seat (must be non-negative)",
    )



class Find_Flight_Schema(BaseModel):
    flight_name: str = Field(..., description="Name of the flight to find")
    journey_date: str = Field(..., description="Journey date in YYYY-MM-DD format")
    journey_time: str = Field(..., description="Journey time in HH:MM format")
