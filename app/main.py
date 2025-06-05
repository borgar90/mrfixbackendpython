# app/main.py

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from .database import engine, Base
from .routers import customers, products, orders, crm
from .auth import authenticate_user, create_access_token
from .schemas import Token

# Opprett alle tabeller basert på modeller
# NB: I produksjon bør man bruke migrasjoner (f.eks. Alembic) i stedet for å kjøre create_all()
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Webshop API",
    description="API for webshop med CRM, Vipps og Bring-integrasjon",
    version="1.0.0"
)

# Inkluder alle routers
app.include_router(customers.router)
app.include_router(products.router)
app.include_router(orders.router)
app.include_router(crm.router)

@app.get("/")
def root():
    """
    Grunnleggende helse-endpoint.
    """
    return {"message": "Webshop API is up and running!"}

@app.post("/token", response_model=Token)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(
        data={"sub": user['username'], "role": user['role']}
    )
    return {"access_token": access_token, "token_type": "bearer"}
