# app/routers/customers.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from .. import crud, schemas
from ..database import get_db
from ..auth import get_current_user, get_current_admin
from ..models import Customer, User

router = APIRouter(
    prefix="/customers",
    tags=["customers"]
)

# Admin-only: list all customers
@router.get("/", response_model=List[schemas.CustomerRead], dependencies=[Depends(get_current_admin)])
def read_customers(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Hent en liste over kunder med paginering.
    """
    return crud.get_customers(db, skip=skip, limit=limit)

# Admin-only: read any customer by ID
@router.get("/{customer_id}", response_model=schemas.CustomerRead, dependencies=[Depends(get_current_admin)])
def read_customer(customer_id: int, db: Session = Depends(get_db)):
    """
    Hent detaljer om én kunde.
    """
    db_customer = crud.get_customer(db, customer_id)
    if not db_customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return db_customer

# Admin-only: create customer
@router.post("/", response_model=schemas.CustomerRead, status_code=201, dependencies=[Depends(get_current_admin)])
def create_customer(customer: schemas.CustomerCreate, db: Session = Depends(get_db)):
    """
    Opprett en ny kunde.
    """
    # Valider at e-post ikke finnes fra før
    existing = db.query(crud.models.Customer).filter(crud.models.Customer.email == customer.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_customer(db, customer)

# Admin-only: update any customer
@router.put("/{customer_id}", response_model=schemas.CustomerRead, dependencies=[Depends(get_current_admin)])
def update_customer(customer_id: int, customer_in: schemas.CustomerCreate, db: Session = Depends(get_db)):
    """
    Oppdater en eksisterende kunde.
    """
    db_customer = crud.update_customer(db, customer_id, customer_in)
    if not db_customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return db_customer

# Admin-only: delete any customer
@router.delete("/{customer_id}", status_code=204, dependencies=[Depends(get_current_admin)])
def delete_customer(customer_id: int, db: Session = Depends(get_db)):
    """
    Slett en kunde.
    """
    crud.delete_customer(db, customer_id)
    return

# Customer: view own profile
@router.get("/me", response_model=schemas.CustomerRead)
def read_own_customer(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Hent din egen kundeprofil.
    """
    customer = db.query(Customer).filter(Customer.email == current_user.email).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer

# Customer: delete/anonymize own data
@router.delete("/me", status_code=204)
def delete_own_customer(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Slett/anonymiser dine egne data i henhold til GDPR.
    """
    customer = db.query(Customer).filter(Customer.email == current_user.email).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    # GDPR: delete personal data
    crud.delete_customer(db, customer.id)
    return

# Admin-only: read a customer with their orders and product details
@router.get("/{customer_id}/orders", response_model=schemas.CustomerRead, dependencies=[Depends(get_current_admin)])
def read_customer_with_orders(customer_id: int, db: Session = Depends(get_db)):
    """
    Fetch a customer and all their orders (including items and full product details).
    """
    db_customer = crud.get_customer_with_orders(db, customer_id)
    if not db_customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return db_customer
