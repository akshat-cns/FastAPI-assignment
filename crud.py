from sqlalchemy.orm import Session
from models import Event, Booking, User
from schemas import EventCreate, EventUpdate, BookingCreate, UserCreate

def get_all_events(db: Session):
    return db.query(Event).all()

def create_event(db: Session, event: EventCreate):
    db_event = Event(**event.model_dump())
    db.add(db_event)
    db.commit()
    db.refresh(db_event)
    return db_event

def update_event(db: Session, event_id: int, event_data: EventUpdate):
    db_event = db.query(Event).filter(Event.id == event_id).first()
    if db_event:
        for key, value in event_data.model_dump(exclude_unset=True).items():
            setattr(db_event, key, value)
        db.commit()
        db.refresh(db_event)
    return db_event

def delete_event(db: Session, event_id: int):
    db_event = db.query(Event).filter(Event.id == event_id).first()
    if db_event:
        db.delete(db_event)
        db.commit()
    return db_event

def get_event_by_id(db: Session, event_id: int):
    return db.query(Event).filter(Event.id == event_id).first()

def book_tickets(db: Session, booking: BookingCreate):
    db_event = db.query(Event).filter(Event.id == booking.event_id).first()
    if db_event and db_event.available_tickets >= booking.tickets_booked:
        db_booking = Booking(**booking.dict())
        db_event.available_tickets -= booking.tickets_booked
        db.add(db_booking)
        db.commit()
        db.refresh(db_booking)
        return db_booking
    return None

def cancel_booking(db: Session, booking_id: int):
    db_booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if db_booking:
        db_event = db.query(Event).filter(Event.id == db_booking.event_id).first()
        if db_event:
            db_event.available_tickets += db_booking.tickets_booked
        db.delete(db_booking)
        db.commit()
    return db_booking

def get_user_by_username(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()

def create_user(db: Session, user:UserCreate):
    db_user = User(username=user.username, hashed_password=user.hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user