import re

from sqlalchemy import Boolean, Column, Integer, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import declared_attr, sessionmaker

from app.settings import DB_URL

SQLALCHEMY_DATABASE_URL = DB_URL


class Mixin:
    id = Column(Integer, primary_key=True, autoincrement=True)
    archive = Column(Boolean, default=False, nullable=False)

    @declared_attr
    def __tablename__(self):
        return f"{re.sub(r'(?<!^)(?=[A-Z])', '_', self.__name__).lower()}"


engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base(cls=Mixin)
metadata = Base.metadata
