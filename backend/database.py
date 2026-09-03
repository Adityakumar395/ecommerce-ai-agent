import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
from pathlib import Path
from dotenv import load_dotenv

# Load variables from .env file reliably
env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=env_path)
load_dotenv()

# Fetch the database URL securely from the environment
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", "")

# Automatically adapt mysql:// to mysql+pymysql:// for SQLAlchemy compatibility
if SQLALCHEMY_DATABASE_URL.startswith("mysql://"):
    SQLALCHEMY_DATABASE_URL = "mysql+pymysql://" + SQLALCHEMY_DATABASE_URL[len("mysql://"):]

# Set up the SQLAlchemy engine with SSL support if connecting to cloud MySQL (TiDB Cloud / Aiven)
connect_args = {}
if "tidbcloud.com" in SQLALCHEMY_DATABASE_URL and "ssl" not in SQLALCHEMY_DATABASE_URL.lower():
    connect_args = {"ssl_verify_cert": True}

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args=connect_args) if connect_args else create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()