# app/routers/crm.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from .. import crud, schemas
from ..database import get_db

router = APIRouter(
    prefix="/crm",
    tags=["crm"]
)

@router.post("/notes", response_model=schemas.CRMNoteRead, status_code=201)
def create_note(note_in: schemas.CRMNoteCreate, db: Session = Depends(get_db)):
    """
    Opprett et CRM-notat for en kunde.
    """
    # Sjekk at kunden finnes
    from ..crud.customers import get_customer
    customer = get_customer(db, note_in.customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return crud.create_crm_note(db, note_in)

@router.get("/notes/{customer_id}", response_model=List[schemas.CRMNoteRead])
def read_notes(customer_id: int, db: Session = Depends(get_db)):
    """
    Hent alle CRM-notater for en gitt kunde.
    """
    return crud.get_notes_for_customer(db, customer_id)
