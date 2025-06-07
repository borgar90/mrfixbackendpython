# app/routers/products.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from .. import crud, schemas
from ..database import get_db
from ..auth import get_current_user, get_current_admin

router = APIRouter(
    prefix="/products",
    tags=["products"]
)

@router.get("/", response_model=List[schemas.ProductRead])
def read_products(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Hent en liste over produkter med paginering.
    """
    return crud.get_products(db, skip=skip, limit=limit)

@router.get("/{product_id}", response_model=schemas.ProductRead)
def read_product(product_id: int, db: Session = Depends(get_db)):
    """
    Hent detaljer om ett produkt.
    """
    db_product = crud.get_product(db, product_id)
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")
    return db_product

@router.post("/", response_model=schemas.ProductRead, status_code=201, dependencies=[Depends(get_current_admin)])
def create_product(product: schemas.ProductCreate, db: Session = Depends(get_db)):
    """
    Opprett et nytt produkt.
    """
    return crud.create_product(db, product)

@router.put("/{product_id}", response_model=schemas.ProductRead, dependencies=[Depends(get_current_admin)])
def update_product(product_id: int, product_in: schemas.ProductCreate, db: Session = Depends(get_db)):
    """
    Oppdater eksisterende produkt.
    """
    db_product = crud.update_product(db, product_id, product_in)
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")
    return db_product

@router.delete("/{product_id}", status_code=204, dependencies=[Depends(get_current_admin)])
def delete_product(product_id: int, db: Session = Depends(get_db)):
    """
    Slett ett produkt.
    """
    crud.delete_product(db, product_id)
    return

@router.post("/{product_id}/stock", response_model=schemas.ProductRead, dependencies=[Depends(get_current_admin)])
def adjust_stock(product_id: int, stock_update: schemas.StockUpdate, db: Session = Depends(get_db)):
    """
    Juster lagerbeholdning for et produkt (positivt for påfyll, negativt for uttak).
    """
    try:
        updated = crud.adjust_product_stock(db, product_id, stock_update.quantity)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    if not updated:
        raise HTTPException(status_code=404, detail="Product not found")
    return updated
