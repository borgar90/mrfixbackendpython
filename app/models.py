from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship
from datetime import datetime, timezone  # include timezone
from .database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(50), nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    # One-to-one link to customer profile
    customer = relationship("Customer", back_populates="user", uselist=False)

class Customer(Base):
    __tablename__ = "customers"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    user = relationship("User", back_populates="customer")
    first_name = Column(String(100), nullable=False, index=True)
    last_name = Column(String(100), nullable=False, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    phone = Column(String(20), nullable=True)
    address = Column(String(255), nullable=True)
    city = Column(String(100), nullable=True)
    postal_code = Column(String(20), nullable=True)
    country = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    orders = relationship("Order", back_populates="customer")
    notes = relationship("CRMNote", back_populates="customer")

class CRMNote(Base):
    __tablename__ = "crm_notes"
    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id", ondelete="CASCADE"), nullable=False)
    note = Column(Text, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    customer = relationship("Customer", back_populates="notes")

class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    price = Column(Float, nullable=False)
    stock = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    order_items = relationship("OrderItem", back_populates="product")
    images = relationship(
        "ProductImage",
        back_populates="product",
        cascade="all, delete-orphan"
    )

    @property
    def thumbnail_url(self) -> str | None:
        """
        Return URL of the product's thumbnail image if set, else the first image or None.
        """
        # Return explicitly flagged thumbnail if available
        for img in self.images:
            if img.is_thumbnail:
                return img.url
        # Fallback: return first image if exists
        if self.images:
            return self.images[0].url
        return None

class Order(Base):
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id", ondelete="SET NULL"), nullable=True)
    total_amount = Column(Float, nullable=False)
    status = Column(String(50), default="pending")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    customer = relationship("Customer", back_populates="orders")
    items = relationship(
        "OrderItem",
        back_populates="order",
        cascade="all, delete-orphan"
    )

class OrderItem(Base):
    __tablename__ = "order_items"
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id", ondelete="CASCADE"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id", ondelete="SET NULL"), nullable=True)
    quantity = Column(Integer, nullable=False)
    price = Column(Float, nullable=False)
    order = relationship("Order", back_populates="items")
    product = relationship("Product", back_populates="order_items")
    __mapper_args__ = {"confirm_deleted_rows": False}

class ProductImage(Base):
    __tablename__ = "product_images"
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id", ondelete="CASCADE"), nullable=False)
    url = Column(String(500), nullable=False)
    is_main = Column(Integer, default=0)  # 1 for main image
    is_thumbnail = Column(Integer, default=0)  # 1 for thumbnail
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    product = relationship("Product", back_populates="images")
