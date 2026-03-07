from fastapi import FastAPI
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from restaurant_service.infrastructure.repositories.restaurant_repository import RestaurantRepository

DATABASE_URL = "postgresql://user:password@localhost/db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

app = FastAPI()

@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(RestaurantRepository.metadata.create_all)

@app.on_event("shutdown")
async def shutdown():
    pass

app.include_router(restaurant_router)