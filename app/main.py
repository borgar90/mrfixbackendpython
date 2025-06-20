# app/main.py

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from .database import engine, Base, get_db, SessionLocal
from sqlalchemy.orm import Session
from .routers import customers, products, orders, crm, users, statistics
from .routers.payment import router as payment_router  # Import payment router directly to avoid attribute error
from .auth import authenticate_user, create_access_token
from .schemas import Token, UserRole
from .database import SessionLocal
import logging
from .models import User
from .crud.users import pwd_context
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
from dotenv import load_dotenv

load_dotenv()

ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "admin")

# Lifespan context: create default admin on startup
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Ensure default admin user exists before the app starts."""
    db = SessionLocal()
    try:
        if not db.query(User).filter(User.email == ADMIN_EMAIL).first():
            hashed = pwd_context.hash("adminpass")
            db_user = User(
                email=ADMIN_EMAIL,
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
# NB: I produksjon bør man bruke migrasjoner (f.eks. Alembic) i stedet av å kjøre create_all()
Base.metadata.create_all(bind=engine)

# In production DB, ensure `user_id` column exists in `customers` table (for shipping data link)
from sqlalchemy import text
if engine.dialect.name != 'sqlite':
    from sqlalchemy import inspect
    inspector = inspect(engine)
    cols = [col['name'] for col in inspector.get_columns('customers')]
    with engine.connect() as conn:
        # Add user_id column if missing
        if 'user_id' not in cols:
            try:
                conn.execute(text(
                    "ALTER TABLE customers ADD COLUMN user_id INTEGER"
                ))
            except Exception:
                pass
        # Add foreign key constraint if missing
        # Note: MySQL constraint names must be unique
        # We'll add FK only if not present
        fks = [fk['constrained_columns'][0] for fk in inspector.get_foreign_keys('customers')]
        if 'user_id' not in fks:
            try:
                conn.execute(text(
                    "ALTER TABLE customers ADD CONSTRAINT fk_customers_user_id FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE"
                ))
            except Exception:
                pass

app = FastAPI(
    title="Webshop API",
    description="API for webshop med CRM, Vipps og Bring-integrasjon",
    version="1.0.0",
    lifespan=lifespan
)

# Allow CORS for local frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],  # React dev servers
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inkluder alle routers
app.include_router(customers.router)
app.include_router(products.router)
app.include_router(orders.router)
app.include_router(crm.router)
app.include_router(users.router)
app.include_router(statistics.router)
# Include payment router
app.include_router(payment_router)

# Serve uploaded images
app.mount(
    "/static",
    StaticFiles(directory="app/static"),
    name="static"
)

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
        token_data = {"sub": ADMIN_EMAIL, "role": UserRole.admin.value}
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
