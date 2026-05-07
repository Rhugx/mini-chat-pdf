from sqlalchemy import Column, Integer, Text
from pgvector.sqlalchemy import Vector

from app.core.database import Base


class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)

    doc_id = Column(Text)

    content = Column(Text)

    embedding = Column(Vector(384))