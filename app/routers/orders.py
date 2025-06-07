# app/routers/orders.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from .. import crud, schemas
from ..database import get_db
from ..auth import get_current_user, get_current_admin

router = APIRouter(
    prefix="/orders",
    tags=["orders"]
)

@router.get("/", response_model=List[schemas.OrderRead], dependencies=[Depends(get_current_user)])
def read_orders(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Hent en liste over ordrer med paginering.
    """
    return crud.get_orders(db, skip=skip, limit=limit)

@router.get("/{order_id}", response_model=schemas.OrderRead, dependencies=[Depends(get_current_user)])
def read_order(order_id: int, db: Session = Depends(get_db)):
    """
    Hent detaljene til én ordre.
    """
    db_order = crud.get_order(db, order_id)
    if not db_order:
        raise HTTPException(status_code=404, detail="Order not found")
    return db_order

@router.post("/", response_model=schemas.OrderRead, status_code=201, dependencies=[Depends(get_current_user)])
def create_order(order_in: schemas.OrderCreate, db: Session = Depends(get_db)):
    """
    Plasser en ny ordre. Returnerer ordre med ordrelinjer.
    """
    try:
        return crud.create_order(db, order_in)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/{order_id}/status", response_model=schemas.OrderRead, dependencies=[Depends(get_current_admin)])
def update_order_status(order_id: int, status: str, db: Session = Depends(get_db)):
    """
    Oppdater status for en eksisterende ordre.
    """
    db_order = crud.update_order_status(db, order_id, status)
    if not db_order:
        raise HTTPException(status_code=404, detail="Order not found")
    return db_order

@router.delete("/{order_id}", status_code=204, dependencies=[Depends(get_current_admin)])
def delete_order(order_id: int, db: Session = Depends(get_db)):
    """
    Slett en ordre basert på ID.
    """
    crud.delete_order(db, order_id)
    return
