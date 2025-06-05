# app/crud/crm.py

from sqlalchemy.orm import Session
from typing import List
from .. import models, schemas

def create_crm_note(db: Session, note_in: schemas.CRMNoteCreate) -> models.CRMNote:
    """
    Opprett et nytt CRM-notat for en kunde.
    """
    db_note = models.CRMNote(
        customer_id=note_in.customer_id,
        note=note_in.note
    )
    db.add(db_note)
    db.commit()
    db.refresh(db_note)
    return db_note

def get_notes_for_customer(db: Session, customer_id: int) -> List[models.CRMNote]:
    """
    Hent alle notater til en spesifikk kunde.
    """
    return db.query(models.CRMNote).filter(models.CRMNote.customer_id == customer_id).all()
