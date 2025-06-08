# Model Reference

Documentation of SQLAlchemy ORM models defined in `app/models.py`.

## User
- **Table**: `users`
- **Fields**:
  - `id` (Integer, PK)
  - `email` (String, unique, indexed)
  - `hashed_password` (String)
  - `role` (String; e.g., `'admin'` or `'customer'`)
  - `created_at` (DateTime, UTC timestamp)
- **Relationships**:
  - `customer`: one-to-one to `Customer` (via `Customer.user_id`)

## Customer
- **Table**: `customers`
- **Fields**:
  - `id` (Integer, PK)
  - `user_id` (Integer, FK → `users.id`, ondelete=CASCADE)
  - `first_name`, `last_name` (String)
  - `email` (String, unique)
  - `phone`, `address`, `city`, `postal_code`, `country` (String, optional)
  - `created_at` (DateTime, UTC timestamp)
- **Relationships**:
  - `user`: back-populates `User.customer`
  - `orders`: one-to-many `Order` records
  - `notes`: one-to-many `CRMNote` records

## CRMNote
- **Table**: `crm_notes`
- **Fields**:
  - `id` (Integer, PK)
  - `customer_id` (Integer, FK → `customers.id`, ondelete=CASCADE)
  - `note` (Text)
  - `created_at` (DateTime, UTC timestamp)
- **Relationships**:
  - `customer`: back-populates `Customer.notes`

## Product
- **Table**: `products`
- **Fields**:
  - `id` (Integer, PK)
  - `name` (String, indexed)
  - `description` (Text, optional)
  - `price` (Float)
  - `stock` (Integer)
  - `created_at` (DateTime, UTC timestamp)
- **Relationships**:
  - `order_items`: one-to-many `OrderItem` records

## Order
- **Table**: `orders`
- **Fields**:
  - `id` (Integer, PK)
  - `customer_id` (Integer, FK → `customers.id`, ondelete=SET NULL)
  - `total_amount` (Float)
  - `status` (String; uses `OrderStatus` enum values)
  - `created_at` (DateTime, UTC timestamp)
- **Relationships**:
  - `customer`: back-populates `Customer.orders`
  - `items`: one-to-many `OrderItem` records (cascade delete-orphan)

## OrderItem
- **Table**: `order_items`
- **Fields**:
  - `id` (Integer, PK)
  - `order_id` (Integer, FK → `orders.id`, ondelete=CASCADE)
  - `product_id` (Integer, FK → `products.id`, ondelete=SET NULL)
  - `quantity` (Integer)
  - `price` (Float; snapshot of unit price)
- **Relationships**:
  - `order`: back-populates `Order.items`
  - `product`: back-populates `Product.order_items`
- **Mapper Args**:
  - `confirm_deleted_rows=False` (optimizes bulk deletes)
