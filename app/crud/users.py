# app/crud/users.py
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from .. import models, schemas

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_user_by_email(db: Session, email: str) -> models.User:
    return db.query(models.User).filter(models.User.email == email).first()


def create_user(db: Session, user_in: schemas.UserCreate) -> models.User:
    hashed_password = pwd_context.hash(user_in.password)
    db_user = models.User(
        email=user_in.email,
        hashed_password=hashed_password,
        role=user_in.role
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()


def update_user(db: Session, user_id: int, user_in: schemas.UserCreate) -> models.User:
    """
    Update an existing user (admin only).
    """
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if not db_user:
        return None
    # Update fields
    db_user.email = user_in.email
    db_user.hashed_password = pwd_context.hash(user_in.password)
    db_user.role = user_in.role
    db.commit()
    db.refresh(db_user)
    return db_user


def delete_user(db: Session, user_id: int) -> None:
    """
    Delete an existing user (admin only).
    """
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if db_user:
        db.delete(db_user)
        db.commit()


def get_user(db: Session, user_id: int) -> models.User:
    """Get a user by its ID."""
    return db.query(models.User).filter(models.User.id == user_id).first()
