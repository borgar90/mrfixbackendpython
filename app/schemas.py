# app/schemas.py

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, EmailStr, ConfigDict  # add ConfigDict import

# ==========================
# CRM-schemas
# ==========================

class CRMNoteCreate(BaseModel):
    customer_id: int
    note: str


class CRMNoteRead(BaseModel):
    id: int
    customer_id: int
    note: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CustomerBase(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    phone: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    postal_code: Optional[str] = None
    country: Optional[str] = None


class CustomerCreate(CustomerBase):
    pass


class CustomerRead(CustomerBase):
    id: int
    created_at: datetime
    notes: List[CRMNoteRead] = []

    model_config = ConfigDict(from_attributes=True)


# ==========================
# Produkt-schemas
# ==========================

class ProductBase(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    stock: int


class ProductCreate(ProductBase):
    pass


class ProductRead(ProductBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ==========================
# Ordre-schemas
# ==========================

class OrderItemBase(BaseModel):
    product_id: int
    quantity: int


class OrderItemCreate(OrderItemBase):
    pass


class OrderItemRead(OrderItemBase):
    id: int
    price: float

    model_config = ConfigDict(from_attributes=True)


class OrderBase(BaseModel):
    customer_id: Optional[int] = None


class OrderCreate(OrderBase):
    items: List[OrderItemCreate]


class OrderRead(OrderBase):
    id: int
    total_amount: float
    status: str
    created_at: datetime
    items: List[OrderItemRead]

    model_config = ConfigDict(from_attributes=True)


# ==========================
# Authentication Schemas
# ==========================
class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None
    role: Optional[str] = None
