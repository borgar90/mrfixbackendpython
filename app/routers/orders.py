# app/routers/orders.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from .. import crud, schemas
from ..database import get_db
from ..auth import get_current_user, get_current_admin
from ..integrations.vipps import VippsClient
from ..schemas import VippsPaymentRequest, VippsPaymentResponse, VippsCallback

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

@router.post("/{order_id}/pay", response_model=VippsPaymentResponse, dependencies=[Depends(get_current_user)])
def pay_order(
    order_id: int,
    payment_req: VippsPaymentRequest,
    db: Session = Depends(get_db)
):
    """
    Initiate a Vipps payment for a pending order.
    """
    # Fetch order
    order = crud.get_order(db, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    if order.status != schemas.OrderStatus.pending.value:
        raise HTTPException(status_code=400, detail="Order is not pending payment")
    # Create Vipps payment with shipping cost
    shipping_cost = 80.0
    total_amount = order.total_amount + shipping_cost
    vipps = VippsClient(sandbox=True)
    try:
        result = vipps.create_payment(
            order_id=order_id,
            amount=total_amount,
            callback_url=payment_req.callback_url,
            shipping=payment_req.shipping.dict()
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return {"data": result}

@router.post("/{order_id}/callback", status_code=204)
def vipps_callback(
    order_id: int,
    callback: schemas.VippsCallback,
    db: Session = Depends(get_db)
):
    """
    Endpoint for Vipps to notify payment status. Updates order status accordingly.
    """
    # Map Vipps transactionStatus to our OrderStatus
    status_map = {
        "AUTHORIZED": schemas.OrderStatus.paid.value,
        "SETTLED": schemas.OrderStatus.paid.value,
        "REJECTED": schemas.OrderStatus.canceled.value
    }
    new_status = status_map.get(callback.transactionStatus.upper())
    if not new_status:
        # ignore unknown statuses
        return
    db_order = crud.update_order_status(db, order_id, new_status)
    if not db_order:
        raise HTTPException(status_code=404, detail="Order not found")
    return

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
