# filepath: app/routers/statistics.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from ..database import get_db
from ..auth import get_current_admin
from ..crud.statistics import get_monthly_sales, get_unprocessed_orders
from ..schemas import MonthlySales, UnprocessedOrder

router = APIRouter(
    prefix="/statistics",
    tags=["statistics"]
)

@router.get("/sales/{year}", response_model=List[MonthlySales], dependencies=[Depends(get_current_admin)])
def read_monthly_sales(year: int, db: Session = Depends(get_db)):
    """
    Hent total salg per måned for et spesifikt år (kun admin).
    """
    return get_monthly_sales(db, year)

@router.get("/unprocessed_orders", response_model=List[UnprocessedOrder], dependencies=[Depends(get_current_admin)])
def read_unprocessed_orders(db: Session = Depends(get_db)):
    """
    Hent alle ubearbeidede ordrer (status 'pending') (kun admin).
    """
    return get_unprocessed_orders(db)
