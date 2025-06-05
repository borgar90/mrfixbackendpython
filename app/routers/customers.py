# app/routers/customers.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from .. import crud, schemas
from ..database import get_db
from ..auth import get_current_user, get_current_admin

router = APIRouter(
    prefix="/customers",
    tags=["customers"]
)

@router.get("/", response_model=List[schemas.CustomerRead], dependencies=[Depends(get_current_user)])
def read_customers(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Hent en liste over kunder med paginering.
    """
    return crud.get_customers(db, skip=skip, limit=limit)

@router.get("/{customer_id}", response_model=schemas.CustomerRead, dependencies=[Depends(get_current_user)])
def read_customer(customer_id: int, db: Session = Depends(get_db)):
    """
    Hent detaljer om én kunde.
    """
    db_customer = crud.get_customer(db, customer_id)
    if not db_customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return db_customer

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

@router.put("/{customer_id}", response_model=schemas.CustomerRead, dependencies=[Depends(get_current_admin)])
def update_customer(customer_id: int, customer_in: schemas.CustomerCreate, db: Session = Depends(get_db)):
    """
    Oppdater en eksisterende kunde.
    """
    db_customer = crud.update_customer(db, customer_id, customer_in)
    if not db_customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return db_customer

@router.delete("/{customer_id}", status_code=204, dependencies=[Depends(get_current_admin)])
def delete_customer(customer_id: int, db: Session = Depends(get_db)):
    """
    Slett en kunde.
    """
    crud.delete_customer(db, customer_id)
    return
