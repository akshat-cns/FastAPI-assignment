from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from schemas import EventResponse, BookingCreate, BookingResponse
from database import get_db
from crud import get_all_events, book_tickets, cancel_booking

user_router = APIRouter()

@user_router.get("/events", response_model=List[EventResponse])
def view_available_events(db: Session = Depends(get_db)):
    events = get_all_events(db)
    return events

@user_router.post("/events/{event_id}/book", response_model=BookingResponse)
def book_event(event_id: int, booking: BookingCreate, db: Session = Depends(get_db)):
    booking.event_id = event_id
    db_booking = book_tickets(db, booking)
    if not db_booking:
        raise HTTPException(status_code=400, detail="Booking failed. Check availability.")
    return db_booking

@user_router.delete("/events/{booking_id}/cancel", response_model=BookingResponse)
def cancel_event_booking(booking_id: int, db: Session = Depends(get_db)):
    db_booking = cancel_booking(db, booking_id)
    if not db_booking:
        raise HTTPException(status_code=404, detail="Booking not found.")
    return db_booking
