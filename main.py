from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from fastapi import Depends
from sqlalchemy.orm import Session
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel
import os
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")



engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()

# --- Table model ---
class DelayedTrain(Base):
    __tablename__ = "delayed_train"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    distance_km = Column(Integer)
    weather_conditions = Column(Text)
    day_of_week = Column(Text)
    time_of_day = Column(Text)
    train_type = Column(Text)
    historical_delay_min = Column(Integer)
    route_congestion = Column(Text)

# --- Pydantic schema for API ---
class TrainSchema(BaseModel):
    distance_km: int
    weather_conditions: str
    day_of_week: str
    time_of_day: str
    train_type: str
    historical_delay_min: int
    route_congestion: str

class TrainOut(TrainSchema):
    id: int
    class Config:
        orm_mode = True

# --- FastAPI app ---
app = FastAPI()

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- Endpoints ---
@app.get("/")
def root():
    return {"message": "Smart Sanchalak API is running!"}

@app.get("/trains", response_model=List[TrainOut])
def get_trains(db: Session = Depends(get_db)):
    return db.query(DelayedTrain).all()

@app.post("/trains", response_model=TrainOut)
def add_train(train: TrainSchema, db: Session = Depends(get_db)):
    try:
        new_train = DelayedTrain(**train.dict())
        db.add(new_train)
        db.commit()
        db.refresh(new_train)
        return new_train
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")