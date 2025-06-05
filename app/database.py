# app/database.py

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv

# Last inn miljøvariabler fra .env
load_dotenv()

# Les konfigurasjon for MySQL fra miljøvariabler
MYSQL_USER = os.getenv("MYSQL_USER", "root")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "")
MYSQL_HOST = os.getenv("MYSQL_HOST", "127.0.0.1")
MYSQL_PORT = os.getenv("MYSQL_PORT", "3306")
MYSQL_DATABASE = os.getenv("MYSQL_DATABASE", "webshop_db")

# bytt ut PyMySQL med mysqlclient om ønskelig: mysql+mysqldb://user:pass@host:port/db
DATABASE_URL = (
    f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@"
    f"{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}"
)

# Opprett SQLAlchemy-engine
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,  # sørger for å teste forbindelsen før bruk
)

# Lag en SessionLocal for dependencies
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base for ORM-modeller
Base = declarative_base()

def get_db():
    """
    Avhengighet for å hente en database-session per forespørsel.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()