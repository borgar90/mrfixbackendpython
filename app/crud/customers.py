# app/crud/customers.py

from sqlalchemy.orm import Session
from typing import List
from .. import models, schemas

def get_customer(db: Session, customer_id: int) -> models.Customer:
    """
    Hent én kunde ut fra ID.
    """
    return db.query(models.Customer).filter(models.Customer.id == customer_id).first()

def get_customers(db: Session, skip: int = 0, limit: int = 100) -> List[models.Customer]:
    """
    Hent flere kunder, med paginering.
    """
    return db.query(models.Customer).offset(skip).limit(limit).all()

def create_customer(db: Session, customer: schemas.CustomerCreate) -> models.Customer:
    """
    Opprett en ny kunde i databasen.
    """
    db_customer = models.Customer(
        first_name=customer.first_name,
        last_name=customer.last_name,
        email=customer.email,
        phone=customer.phone,
        address=customer.address,
        city=customer.city,
        postal_code=customer.postal_code,
        country=customer.country,
    )
    db.add(db_customer)
    db.commit()
    db.refresh(db_customer)
    return db_customer

def update_customer(db: Session, customer_id: int, updates: schemas.CustomerCreate) -> models.Customer:
    """
    Oppdater eksisterende kunde basert på ID.
    """
    db_customer = get_customer(db, customer_id)
    if not db_customer:
        return None
    for field, value in updates.model_dump(exclude_unset=True).items():
        setattr(db_customer, field, value)
    db.commit()
    db.refresh(db_customer)
    return db_customer

def delete_customer(db: Session, customer_id: int) -> None:
    """
    Slett kunde basert på ID.
    """
    db_customer = get_customer(db, customer_id)
    if db_customer:
        db.delete(db_customer)
        db.commit()
