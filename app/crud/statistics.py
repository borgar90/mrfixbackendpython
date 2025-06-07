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
