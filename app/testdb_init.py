from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base
from app.models import Product, Customer, Order, User  # Import User model

# Define the test database URL
test_db_url = "sqlite:///testdb.sqlite"
engine = create_engine(test_db_url, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def initialize_testdb():
    """
    Initialize the test database and populate it with dummy data if empty.
    """
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        # Check if the database is already populated
        if not db.query(Product).first():
            # Add dummy products
            products = [
                Product(name="Product A", description="Description A", price=10.0, stock=100),
                Product(name="Product B", description="Description B", price=20.0, stock=200),
                Product(name="Product C", description="Description C", price=30.0, stock=300),
            ]
            db.add_all(products)

        if not db.query(User).first():
            # Add dummy users
            users = [
                User(email="user1@example.com", hashed_password="hashedpassword1", role="customer"),
                User(email="user2@example.com", hashed_password="hashedpassword2", role="customer"),
            ]
            db.add_all(users)
            db.commit()

        # Fetch user IDs for associating with customers
        user1_id = db.query(User).filter_by(email="user1@example.com").first().id
        user2_id = db.query(User).filter_by(email="user2@example.com").first().id

        if not db.query(Customer).first():
            # Add dummy customers
            customers = [
                Customer(user_id=user1_id, first_name="John", last_name="Doe", email="john.doe@example.com"),
                Customer(user_id=user2_id, first_name="Jane", last_name="Smith", email="jane.smith@example.com"),
            ]
            db.add_all(customers)

        if not db.query(Order).first():
            # Add dummy orders
            orders = [
                Order(customer_id=user1_id, total_amount=100.0, status="pending"),
                Order(customer_id=user2_id, total_amount=200.0, status="completed"),
            ]
            db.add_all(orders)

        db.commit()
    finally:
        db.close()

if __name__ == "__main__":
    initialize_testdb()
