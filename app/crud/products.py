# app/crud/products.py

from sqlalchemy.orm import Session
from typing import List
from .. import models, schemas

def get_product(db: Session, product_id: int) -> models.Product:
    """
    Hent ett produkt ut fra ID.
    """
    return db.query(models.Product).filter(models.Product.id == product_id).first()

def get_products(db: Session, skip: int = 0, limit: int = 100) -> List[models.Product]:
    """
    Hent flere produkter, med paginering.
    """
    return db.query(models.Product).offset(skip).limit(limit).all()

def create_product(db: Session, product: schemas.ProductCreate) -> models.Product:
    """
    Opprett et nytt produkt.
    """
    db_product = models.Product(
        name=product.name,
        description=product.description,
        price=product.price,
        stock=product.stock,
    )
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product

def update_product(db: Session, product_id: int, updates: schemas.ProductCreate) -> models.Product:
    """
    Oppdater et eksisterende produkt.
    """
    db_product = get_product(db, product_id)
    if not db_product:
        return None
    for field, value in updates.model_dump(exclude_unset=True).items():
        setattr(db_product, field, value)
    db.commit()
    db.refresh(db_product)
    return db_product

def delete_product(db: Session, product_id: int) -> None:
    """
    Slett et produkt basert på ID.
    """
    db_product = get_product(db, product_id)
    if db_product:
        db.delete(db_product)
        db.commit()

def adjust_product_stock(db: Session, product_id: int, quantity: int) -> models.Product:
    """
    Adjust the stock of a product by a given quantity (positive to add, negative to remove).
    """
    db_product = get_product(db, product_id)
    if not db_product:
        return None
    new_stock = db_product.stock + quantity
    if new_stock < 0:
        raise ValueError(f"Stock cannot be negative; attempted adjustment {quantity}")
    db_product.stock = new_stock
    db.commit()
    db.refresh(db_product)
    return db_product
