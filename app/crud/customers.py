# app/crud/customers.py

import uuid
from sqlalchemy.orm import Session, joinedload
from typing import List
from .. import models, schemas
from .users import create_user as create_user_crud
from ..schemas import UserCreate, UserRole

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
    Opprett en ny kunde i databasen. Hvis user_id ikke oppgitt, opprett en tilhørende User.
    """
    # Ensure linked user exists or create new one
    if customer.user_id:
        user_id = customer.user_id
    else:
        # Create a new auth User for this customer
        # Use temporary random password
        temp_pw = uuid.uuid4().hex
        user_in = UserCreate(email=customer.email, password=temp_pw, role=UserRole.customer)
        db_user = create_user_crud(db, user_in)
        user_id = db_user.id
    # Create Customer record linked to user_id
    db_customer = models.Customer(
        user_id=user_id,
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

def get_customer_with_orders(db: Session, customer_id: int) -> models.Customer:
    """
    Fetch a customer and their orders (with items and full product details) by customer ID.
    """
    return (
        db.query(models.Customer)
        .options(
            joinedload(models.Customer.orders)
            .joinedload(models.Order.items)
            .joinedload(models.OrderItem.product)
        )
        .filter(models.Customer.id == customer_id)
        .first()
    )
