# app/crud/orders.py

from sqlalchemy.orm import Session
from typing import List
from .. import models, schemas
from sqlalchemy.exc import SQLAlchemyError
from ..schemas import OrderStatus  # import enum

def create_order(db: Session, order_in: schemas.OrderCreate) -> models.Order:
    """
    Opprett en ny ordre, inkludert ordrelinjer og oppdatering av lagerbeholdning.
    """
    # Ensure the customer exists
    customer = db.query(models.Customer).filter(models.Customer.id == order_in.customer_id).first()
    if not customer:
        raise ValueError(f"Customer with id {order_in.customer_id} not found")
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
        status=OrderStatus.pending.value  # default pending
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
    # Validate status value
    try:
        status_enum = OrderStatus(status)
    except ValueError:
        raise ValueError(f"Invalid status '{status}'")
    db_order = get_order(db, order_id)
    if db_order:
        db_order.status = status_enum.value
        db.commit()
        db.refresh(db_order)
    return db_order

def delete_order(db: Session, order_id: int) -> None:
    """
    Slett en eksisterende ordre basert på ID.
    """
    db_order = get_order(db, order_id)
    if db_order:
        # Restore product stock before deleting order items
        for item in db_order.items:
            if item.product:
                item.product.stock += item.quantity
        # Delete order items (disable session synchronization to avoid SAWarning)
        db.query(models.OrderItem).filter(models.OrderItem.order_id == order_id).delete(synchronize_session=False)
        # Delete the order itself
        db.delete(db_order)
        db.commit()
