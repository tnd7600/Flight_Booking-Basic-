from fastapi import FastAPI
from src.routers.user import user_router
from src.routers.flights import flight_router
from src.routers.admin import admin_router
from src.routers.booking import booking_router
app = FastAPI()


app.include_router(user_router)
app.include_router(flight_router)
app.include_router(admin_router) 
app.include_router(booking_router) 