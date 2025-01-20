from pydantic import BaseModel, Field



class Date_Route_Passengers_Select_Schema(BaseModel):
    journey_date: str = Field(..., description="Journey date in YYYY-MM-DD format.")
    start_point: str = Field(..., description="Starting point of the journey.")
    end_point: str = Field(..., description="Ending point of the journey.")
    no_of_adults: int = Field(
        ..., ge=0, description="Number of adult passengers (must be non-negative)."
    )
    no_of_children: int = Field(
        ..., ge=0, description="Number of child passengers (must be non-negative)."
    )
    no_of_infants: int = Field(
        ..., ge=0, description="Number of infant passengers (must be non-negative)."
    )

    class Config:
        json_schema_extra = {
            "example": {
                "journey_date": "2024-12-25",
                "start_point": "New York",
                "end_point": "Los Angeles",
                "no_of_adults": 2,
                "no_of_children": 1,
                "no_of_infants": 0,
            }
        }



class Available_Flight_Schema(BaseModel):
    journey_date: str = Field(..., description="Journey date in YYYY-MM-DD format.")
    flight_name: str = Field(..., description="Name of the flight.")
    journey_time: str = Field(..., description="Journey time in HH:MM format.")

    class Config:
        json_schema_extra = {
            "example": {
                "journey_date": "2024-12-25",
                "flight_name": "Delta Airlines DL123",
                "journey_time": "14:30"
            }
        }
