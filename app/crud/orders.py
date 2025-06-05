# app/crud/orders.py

from sqlalchemy.orm import Session
from typing import List
from .. import models, schemas
from sqlalchemy.exc import SQLAlchemyError

def create_order(db: Session, order_in: schemas.OrderCreate) -> models.Order:
    """
    Opprett en ny ordre, inkludert ordrelinjer og oppdatering av lagerbeholdning.
    """
    # Kalkuler totalbeløp basert på produktpriser og antall
    total = 0.0
    items_data = []
    for item in order_in.items:
        product = db.query(models.Product).filter(models.Product.id == item.product_id).first()
        if not product:
            raise ValueError(f"Product with id {item.product_id} not found")
        if product.stock < item.quantity:
            raise ValueError(f"Not enough stock for product {product.name}")
        total += product.price * item.quantity
        items_data.append((product, item.quantity, product.price))

    # Opprett ordre-entity
    db_order = models.Order(
        customer_id=order_in.customer_id,
        total_amount=total,
        status="pending"
    )
    db.add(db_order)
    db.flush()  # tvinger SQLAlchemy til å gi db_order en ID uten commit

    # Opprett ordrelinjer og oppdater lager
    for product, qty, price in items_data:
        order_item = models.OrderItem(
            order_id=db_order.id,
            product_id=product.id,
            quantity=qty,
            price=price
        )
        product.stock -= qty  # trekk fra lagerbeholdning
        db.add(order_item)

    db.commit()
    db.refresh(db_order)
    return db_order

def get_order(db: Session, order_id: int) -> models.Order:
    """
    Hent en ordre basert på ID.
    """
    return db.query(models.Order).filter(models.Order.id == order_id).first()

def get_orders(db: Session, skip: int = 0, limit: int = 100) -> List[models.Order]:
    """
    Hent flere ordrer, med paginering.
    """
    return db.query(models.Order).offset(skip).limit(limit).all()

def update_order_status(db: Session, order_id: int, status: str) -> models.Order:
    """
    Oppdater status for en eksisterende ordre.
    """
    db_order = get_order(db, order_id)
    if db_order:
        db_order.status = status
        db.commit()
        db.refresh(db_order)
    return db_order

def delete_order(db: Session, order_id: int) -> None:
    """
    Slett en eksisterende ordre basert på ID.
    """
    db_order = get_order(db, order_id)
    if db_order:
        # First delete associated order items to satisfy NOT NULL constraints
        db.query(models.OrderItem).filter(models.OrderItem.order_id == order_id).delete()
        db.delete(db_order)
        db.commit()
