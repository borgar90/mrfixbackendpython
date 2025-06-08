# app/routers/products.py

from fastapi import APIRouter, Depends, HTTPException, File, UploadFile
from sqlalchemy.orm import Session
from typing import List
import os
import uuid

from .. import crud, schemas
from ..database import get_db
from ..auth import get_current_user, get_current_admin
from fastapi import status

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
    new_prod = crud.create_product(db, product)
    # Create per-product media directory
    slug = ''.join(e for e in new_prod.name.lower() if e.isalnum())[:10]
    folder_name = f"{slug}_{new_prod.id}"
    media_dir = os.path.join(os.getcwd(), "app", "static", folder_name, "media")
    os.makedirs(media_dir, exist_ok=True)
    return new_prod

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

# ==========================
# Image management endpoints
# ==========================

@router.get("/{product_id}/images", response_model=List[schemas.ProductImageRead])
def list_images(product_id: int, db: Session = Depends(get_db)):
    images = crud.get_product_images(db, product_id)
    return images

@router.get("/{product_id}/images/{image_id}", response_model=schemas.ProductImageRead)
def get_image(product_id: int, image_id: int, db: Session = Depends(get_db)):
    image = crud.get_product_image(db, product_id, image_id)
    if not image:
        raise HTTPException(status_code=404, detail="Image not found")
    return image

@router.post("/{product_id}/images", response_model=schemas.ProductImageRead, status_code=status.HTTP_201_CREATED)
def upload_image(product_id: int, file: UploadFile = File(...), db: Session = Depends(get_db)):
    # Validate product exists
    prod = crud.get_product(db, product_id)
    if not prod:
        raise HTTPException(status_code=404, detail="Product not found")
    # Ensure per-product media folder exists
    slug = ''.join(e for e in prod.name.lower() if e.isalnum())[:10]
    folder_name = f"{slug}_{product_id}"
    media_dir = os.path.join(os.getcwd(), "app", "static", folder_name, "media")
    os.makedirs(media_dir, exist_ok=True)
    # Save file in product media folder
    ext = os.path.splitext(file.filename)[1]
    filename = f"{uuid.uuid4().hex}{ext}"
    dest_path = os.path.join(media_dir, filename)
    with open(dest_path, "wb") as f:
        f.write(file.file.read())
    url = f"/static/{folder_name}/media/{filename}"
    # Create DB record
    img = crud.create_product_image(db, product_id, url)
    return img

@router.put("/{product_id}/images/{image_id}", response_model=schemas.ProductImageRead, dependencies=[Depends(get_current_admin)])
def update_image(product_id: int, image_id: int, update: schemas.ProductImageUpdate, db: Session = Depends(get_db)):
    img = crud.update_product_image(db, product_id, image_id, update.is_main, update.is_thumbnail)
    if not img:
        raise HTTPException(status_code=404, detail="Image not found or no changes applied")
    return img

@router.delete("/{product_id}/images/{image_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(get_current_admin)])
def delete_image(product_id: int, image_id: int, db: Session = Depends(get_db)):
    img = crud.get_product_image(db, product_id, image_id)
    if not img:
        raise HTTPException(status_code=404, detail="Image not found")
    # Remove file
    path = os.path.join(os.getcwd(), "app", img.url.lstrip("/"))
    if os.path.exists(path):
        os.remove(path)
    crud.delete_product_image(db, product_id, image_id)
    return
