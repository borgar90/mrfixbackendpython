# app/schemas.py

from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, EmailStr, ConfigDict  # add ConfigDict import
from enum import Enum  # new import

# Define order status enum
class OrderStatus(str, Enum):
    pending = "pending"
    paid = "paid"
    shipped = "shipped"
    canceled = "canceled"
    refunded = "refunded"


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
    user_id: Optional[int] = None  # link to authentication user; auto-created if not provided


class CustomerRead(CustomerBase):
    id: int
    created_at: datetime
    notes: List[CRMNoteRead] = []
    orders: List["CustomerOrderRead"] = []  # Include customer's orders

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
    thumbnail_url: Optional[str] = None
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
    product: ProductRead  # Include full product details

    model_config = ConfigDict(from_attributes=True)


# Schema used for including orders under a customer without causing a recursive customer field
class CustomerOrderRead(BaseModel):
    id: int
    total_amount: float
    status: "OrderStatus"
    created_at: datetime
    items: List[OrderItemRead]

    model_config = ConfigDict(from_attributes=True)


class OrderBase(BaseModel):
    customer_id: int  # customer is required for every order


class OrderCreate(OrderBase):
    items: List[OrderItemCreate]


class OrderRead(OrderBase):
    id: int
    total_amount: float
    status: OrderStatus  # constrained to valid statuses
    created_at: datetime
    items: List[OrderItemRead]
    customer: CustomerRead  # Include customer details

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


# ==========================
# User roles
# ==========================
class UserRole(str, Enum):
    admin = "admin"
    customer = "customer"
    user = "user"


# ==========================
# Shipping Information schema
# ==========================
class ShippingInfo(BaseModel):
    first_name: str
    last_name: str
    address: str
    city: str
    postal_code: str
    country: str
    email: EmailStr
    phone: Optional[str] = None


# ==========================
# User schemas
# ==========================
class UserBase(BaseModel):
    email: str
    role: UserRole  # role must be either 'admin' or 'customer'


class UserCreate(UserBase):
    password: str
    # Optional initial shipping info for customer
    shipping: Optional[ShippingInfo] = None


class UserRead(UserBase):
    id: int
    created_at: datetime
    # Include linked customer/shipping profile when available
    customer: Optional[CustomerRead] = None

    model_config = ConfigDict(from_attributes=True)


# ==========================
# Statistics schemas
# ==========================
class MonthlySales(BaseModel):
    month: int
    total: float


class UnprocessedOrder(  # for clarity, reuse OrderRead schema for full order data
    BaseModel
):
    id: int
    customer_id: int
    total_amount: float
    status: OrderStatus
    created_at: datetime
    customer: CustomerRead  # full customer details
    items: List[OrderItemRead]  # include order lines with product details

    model_config = ConfigDict(from_attributes=True)


class StockUpdate(BaseModel):
    """
    Model for adjusting product stock (positive or negative quantity).
    """

    quantity: int


class CountResponse(BaseModel):
    count: int


class RevenueResponse(BaseModel):
    total: float


# ==========================
# Product Image schemas
# ==========================
class ProductImageBase(BaseModel):
    url: str
    is_main: Optional[bool] = False
    is_thumbnail: Optional[bool] = False


class ProductImageCreate(ProductImageBase):
    pass


class ProductImageRead(ProductImageBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ProductImageUpdate(BaseModel):
    is_main: Optional[bool]
    is_thumbnail: Optional[bool]


# ==========================
# Vipps payment schemas
# ==========================

class VippsPaymentRequest(BaseModel):
    callback_url: str
    # Shipping information required for unauthenticated payments
    shipping: ShippingInfo


class VippsPaymentResponse(BaseModel):
    data: Dict[str, Any]


class VippsCallback(BaseModel):
    transactionStatus: str
    orderId: Optional[str] = None


class VippsInitiateRequest(BaseModel):
    order_id: int
    callback_url: str
    shipping: ShippingInfo


# ==========================
# Stripe payment schemas
# ==========================

class StripeInitiateRequest(BaseModel):
    order_id: int
    callback_url: str
    shipping: ShippingInfo


class StripePaymentResponse(BaseModel):
    data: Dict[str, Any]


class StripeWebhook(BaseModel):
    type: str
    data: Dict[str, Any]
