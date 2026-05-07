from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base

DATABASE_URL = "postgresql://postgres:postgres@postgres:5432/vectordb"

engine = create_engine(DATABASE_URL)

Base = declarative_base()