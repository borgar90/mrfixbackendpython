# app/main.py

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from .database import engine, Base, get_db, SessionLocal
from sqlalchemy.orm import Session
from .routers import customers, products, orders, crm, users, statistics
from .auth import authenticate_user, create_access_token
from .schemas import Token, UserRole
from .database import SessionLocal
import logging
from .models import User
from .crud.users import pwd_context
from contextlib import asynccontextmanager

# Lifespan context: create default admin on startup
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Ensure default admin user exists before the app starts."""
    db = SessionLocal()
    try:
        if not db.query(User).filter(User.email == "admin").first():
            hashed = pwd_context.hash("adminpass")
            db_user = User(
                email="admin",
                hashed_password=hashed,
                role=UserRole.admin.value
            )
            db.add(db_user)
            db.commit()
            logging.info("Default admin user created.")
    finally:
        db.close()
    yield

# Opprett alle tabeller basert på modeller
# NB: I produksjon bør man bruke migrasjoner (f.eks. Alembic) i stedet for å kjøre create_all()
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Webshop API",
    description="API for webshop med CRM, Vipps og Bring-integrasjon",
    version="1.0.0",
    lifespan=lifespan
)

# Inkluder alle routers
app.include_router(customers.router)
app.include_router(products.router)
app.include_router(orders.router)
app.include_router(crm.router)
app.include_router(users.router)
app.include_router(statistics.router)

@app.get("/")
def root():
    """
    Grunnleggende helse-endpoint.
    """
    return {"message": "Webshop API is up and running!"}

@app.post("/token", response_model=Token)
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    # Special-case admin credentials without DB
    if form_data.username == "admin" and form_data.password == "adminpass":
        token_data = {"sub": "admin", "role": UserRole.admin.value}
        access_token = create_access_token(data=token_data)
        return {"access_token": access_token, "token_type": "bearer"}
    # Regular user authentication
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(
        data={"sub": user.email, "role": user.role}
    )
    return {"access_token": access_token, "token_type": "bearer"}
