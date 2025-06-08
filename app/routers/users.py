# app/routers/users.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from .. import crud, schemas
from ..database import get_db
from ..auth import get_current_admin, get_current_user
from .. import models

router = APIRouter(
    prefix="/users",
    tags=["users"]
)

@router.post("/", response_model=schemas.UserRead, status_code=status.HTTP_201_CREATED)
def create_user(user_in: schemas.UserCreate, db: Session = Depends(get_db)):
    """Register a new user (admin or customer)"""
    existing = crud.get_user_by_email(db, user_in.email)
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    # Create the user
    db_user = crud.create_user(db, user_in)
    # If customer role and shipping data provided, create customer profile
    if db_user.role == schemas.UserRole.customer.value and user_in.shipping:
        shipping = user_in.shipping
        cust_in = schemas.CustomerCreate(
            user_id=db_user.id,
            first_name=shipping.first_name,
            last_name=shipping.last_name,
            email=shipping.email,
            phone=shipping.phone,
            address=shipping.address,
            city=shipping.city,
            postal_code=shipping.postal_code,
            country=shipping.country
        )
        crud.create_customer(db, cust_in)
    return db_user

@router.get("/", response_model=List[schemas.UserRead], dependencies=[Depends(get_current_admin)])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Admin: list all users"""
    return crud.get_users(db, skip=skip, limit=limit)

@router.get("/me", response_model=schemas.UserRead)
def read_current_user(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Retrieve profile of the current authenticated user, including shipping/customer data"""
    # Load fresh user with relationships
    db_user = crud.get_user(db, current_user.id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

@router.get("/{user_id}", response_model=schemas.UserRead, dependencies=[Depends(get_current_admin)])
def read_user(user_id: int, db: Session = Depends(get_db)):
    """Admin: read user by ID"""
    db_user = crud.get_user(db, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

@router.put("/{user_id}", response_model=schemas.UserRead, dependencies=[Depends(get_current_admin)])
def update_user(user_id: int, user_in: schemas.UserCreate, db: Session = Depends(get_db)):
    """Admin: update existing user"""
    db_user = crud.update_user(db, user_id, user_in)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(get_current_admin)])
def delete_user(user_id: int, db: Session = Depends(get_db)):
    """Admin: delete user"""
    crud.delete_user(db, user_id)
    return
