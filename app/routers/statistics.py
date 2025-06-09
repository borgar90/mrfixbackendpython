# filepath: app/routers/statistics.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from ..database import get_db
from ..auth import get_current_admin
from ..crud.statistics import (
    get_monthly_sales,
    get_unprocessed_orders,
    get_total_users,
    get_paid_unprocessed_count,
    get_total_orders,
    get_total_revenue,
)
from ..schemas import MonthlySales, UnprocessedOrder, CountResponse, RevenueResponse

router = APIRouter(
    prefix="/statistics",
    tags=["statistics"]
)

@router.get("/sales/{year}", response_model=List[MonthlySales], dependencies=[Depends(get_current_admin)])
def read_monthly_sales(year: int, db: Session = Depends(get_db)):
    """
    Get total sales per month for a specific year (only paid orders) (admin only).
    """
    return get_monthly_sales(db, year)

@router.get("/unprocessed_orders", response_model=List[UnprocessedOrder], dependencies=[Depends(get_current_admin)])
def read_unprocessed_orders(db: Session = Depends(get_db)):
    """
    Get all orders that have been successfully paid but not yet shipped (admin only).
    """
    return get_unprocessed_orders(db)

@router.get("/total_users", response_model=CountResponse, dependencies=[Depends(get_current_admin)])
def read_total_users(db: Session = Depends(get_db)):
    """
    Return total number of registered users (admin only).
    """
    count = get_total_users(db)
    return {"count": count}

@router.get("/paid_unprocessed_count", response_model=CountResponse, dependencies=[Depends(get_current_admin)])
def read_paid_unprocessed_count(db: Session = Depends(get_db)):
    """
    Return count of paid orders not yet processed (admin only).
    """
    count = get_paid_unprocessed_count(db)
    return {"count": count}

@router.get("/total_orders", response_model=CountResponse, dependencies=[Depends(get_current_admin)])
def read_total_orders(db: Session = Depends(get_db)):
    """
    Return total number of orders placed (admin only).
    """
    count = get_total_orders(db)
    return {"count": count}

@router.get("/total_revenue", response_model=RevenueResponse, dependencies=[Depends(get_current_admin)])
def read_total_revenue(db: Session = Depends(get_db)):
    """
    Return total revenue from paid orders (admin only).
    """
    total = get_total_revenue(db)
    return {"total": total}
