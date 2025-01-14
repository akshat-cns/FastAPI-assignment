from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from schemas import EventCreate, EventUpdate, EventResponse
from database import get_db
from crud import get_all_events, create_event, update_event, delete_event
import auth

admin_router = APIRouter()

@admin_router.get("/events", response_model=List[EventResponse])
def view_all_events(db: Session = Depends(get_db)):
    if(auth.get_current_user.is_admin):
        events = get_all_events(db)
        return events
    raise HTTPException(
        detail="You are not authorised"
    )

@admin_router.post("/events", response_model=EventResponse)
def add_new_event(event: EventCreate, db: Session = Depends(get_db)):
    if(auth.get_current_user.is_admin):
        db_event = create_event(db, event)
        return db_event
    raise HTTPException(
        detail="You are not authorised"
    )

@admin_router.put("/events/{event_id}", response_model=EventResponse)
def update_event_details(event_id: int, event: EventUpdate, db: Session = Depends(get_db)):
    if(auth.get_current_user.is_admin):
        db_event = update_event(db, event_id, event)
        if not db_event:
            raise HTTPException(status_code=404, detail="Event not found.")
        return db_event
    raise HTTPException(
        detail="You are not authorised"
    )

@admin_router.delete("/events/{event_id}", response_model=EventResponse)
def delete_event_details(event_id: int, db: Session = Depends(get_db)):
    if(auth.get_current_user.is_admin):
        db_event = delete_event(db, event_id)
        if not db_event:
            raise HTTPException(status_code=404, detail="Event not found.")
        return db_event
    raise HTTPException(
        detail="You are not authorised"
    )