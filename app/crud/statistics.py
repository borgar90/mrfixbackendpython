# filepath: app/crud/statistics.py
from sqlalchemy.orm import Session
from sqlalchemy import extract, func
from typing import List, Tuple

from .. import models
from ..schemas import OrderStatus


def get_monthly_sales(db: Session, year: int) -> List[Tuple[int, float]]:
    """
    Return total sales per month for a given year.
    """
    # Aggregate total_amount by month for the specified year
    results = (
        db.query(
            extract('month', models.Order.created_at).label('month'),
            func.coalesce(func.sum(models.Order.total_amount), 0).label('total')
        )
        .filter(extract('year', models.Order.created_at) == year)
        .group_by('month')
        .order_by('month')
        .all()
    )
    # Convert SQLAlchemy Row objects to simple tuples
    return [(int(month), float(total)) for month, total in results]


def get_unprocessed_orders(db: Session) -> List[models.Order]:
    """
    Return all orders with status 'pending' or unprocessed.
    """
    return (
        db.query(models.Order)
        .filter(models.Order.status == OrderStatus.pending.value)
        .all()
    )


def get_total_users(db: Session) -> int:
    """
    Return total number of registered users.
    """
    return db.query(func.count(models.User.id)).scalar() or 0


def get_paid_unprocessed_count(db: Session) -> int:
    """
    Return count of orders that are paid but not yet processed (if processing status differs, here we treat paid as unprocessed).
    """
    return (
        db.query(func.count(models.Order.id))
        .filter(models.Order.status == OrderStatus.paid.value)
        .scalar() or 0
    )


def get_total_orders(db: Session) -> int:
    """
    Return total number of orders placed.
    """
    return db.query(func.count(models.Order.id)).scalar() or 0


def get_total_revenue(db: Session) -> float:
    """
    Return total revenue of orders with status paid (excluding refunded).
    """
    total = (
        db.query(func.coalesce(func.sum(models.Order.total_amount), 0.0))
        .filter(models.Order.status == OrderStatus.paid.value)
        .scalar()
    )
    return float(total)
