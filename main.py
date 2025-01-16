from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from database import SessionLocal,Base,engine
from admin_routes import admin_router
from user_routes import user_router
import schemas,auth,crud,models

Base.metadata.create_all(bind=engine)

app = FastAPI()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

app.include_router(admin_router, prefix="/admin", tags=["Admin"])
app.include_router(user_router, tags=["User"])

@app.get("/")
def root():
    return {"message": "Welcome to the Event Booking System!"}

@app.post("/register")
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    hashed_password = auth.get_password_hash(user.password)
    user_data = models.User(username=user.username, hashed_password=hashed_password, is_admin=False)
    db.add(user_data)
    db.commit()
    db.refresh(user_data)
    
    return {"message": f"User '{user.username}' registered successfully."}

@app.post("/login", response_model=schemas.LoginResponse)
def login(request: schemas.LoginRequest, db: Session = Depends(get_db)):
    user = crud.get_user_by_username(db=db, username=request.username)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )

    if not auth.verify_password(request.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )

    access_token = auth.create_access_token(data={"sub": user.username})
    return schemas.LoginResponse(access_token=access_token)