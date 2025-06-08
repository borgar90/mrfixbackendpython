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

def get_product_image(db: Session, product_id: int, image_id: int) -> models.ProductImage:
    """Get one product image by ID for a given product."""
    return (
        db.query(models.ProductImage)
        .filter(
            models.ProductImage.product_id == product_id,
            models.ProductImage.id == image_id
        )
        .first()
    )

def get_product_images(db: Session, product_id: int) -> list[models.ProductImage]:
    """List all images for a given product."""
    return (
        db.query(models.ProductImage)
        .filter(models.ProductImage.product_id == product_id)
        .all()
    )

def create_product_image(db: Session, product_id: int, url: str, is_main: bool=False, is_thumbnail: bool=False) -> models.ProductImage:
    """Create a new image record for a product."""
    db_image = models.ProductImage(
        product_id=product_id,
        url=url,
        is_main=int(is_main),
        is_thumbnail=int(is_thumbnail)
    )
    db.add(db_image)
    db.commit()
    db.refresh(db_image)
    return db_image

def update_product_image(db: Session, product_id: int, image_id: int, is_main: bool=None, is_thumbnail: bool=None) -> models.ProductImage:
    """Update flags for a product image."""
    db_image = get_product_image(db, product_id, image_id)
    if not db_image:
        return None
    if is_main is not None:
        db_image.is_main = int(is_main)
    if is_thumbnail is not None:
        db_image.is_thumbnail = int(is_thumbnail)
    db.commit()
    db.refresh(db_image)
    return db_image

def delete_product_image(db: Session, product_id: int, image_id: int) -> None:
    """Delete an image from a product."""
    db_image = get_product_image(db, product_id, image_id)
    if db_image:
        db.delete(db_image)
        db.commit()
