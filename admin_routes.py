from fastapi import APIRouter, Depends, Security, HTTPException
from sqlalchemy.orm import Session
from typing import List
from schemas import EventCreate, EventUpdate, EventResponse, User
from database import get_db
from crud import get_all_events, create_event, update_event, delete_event
from auth import get_current_admin_user

admin_router = APIRouter()

@admin_router.get("/events", response_model=List[EventResponse])
def view_all_events(db: Session = Depends(get_db),current_admin: User = Security(get_current_admin_user)):
    events = get_all_events(db)
    return events

@admin_router.post("/events", response_model=EventResponse)
def add_new_event(event: EventCreate, db: Session = Depends(get_db),current_admin: User = Security(get_current_admin_user)):
    db_event = create_event(db, event)
    return db_event

@admin_router.put("/events/{event_id}", response_model=EventResponse)
def update_event_details(event_id: int, event: EventUpdate, db: Session = Depends(get_db),current_admin: User = Security    (get_current_admin_user)):  
    db_event = update_event(db, event_id, event)
    if not db_event:
        raise HTTPException(status_code=404, detail="Event not found.")
    return db_event

@admin_router.delete("/events/{event_id}", response_model=EventResponse)
def delete_event_details(event_id: int, db: Session = Depends(get_db), current_admin: User = Security(get_current_admin_user)):
    db_event = delete_event(db, event_id)
    if not db_event:
        raise HTTPException(status_code=404, detail="Event not found.")
    return db_event