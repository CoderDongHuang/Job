from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from sqlalchemy.types import TypeDecorator, TEXT
import json

Base = declarative_base()

class JSONEncodedDict(TypeDecorator):
    """Represents an immutable structure as a json-encoded string."""
    impl = TEXT

    def process_bind_param(self, value, dialect):
        if value is not None:
            return json.dumps(value, ensure_ascii=False)
        return value

    def process_result_value(self, value, dialect):
        if value is not None:
            try:
                return json.loads(value)
            except (ValueError, TypeError):
                return value
        return value

class Job(Base):
    __tablename__ = "jobs"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), index=True)
    company = Column(String(255), index=True)
    city = Column(String(100), index=True)
    salary_min = Column(Integer)
    salary_max = Column(Integer)
    experience_required = Column(String(50))
    education_required = Column(String(50))
    description = Column(Text)
    requirements = Column(Text)
    category = Column(String(100), index=True)
    tags = Column(JSONEncodedDict)  # 存储技能标签列表
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, index=True)
    email = Column(String(255), unique=True, index=True)
    full_name = Column(String(255))
    hashed_password = Column(String(255))
    created_at = Column(DateTime, server_default=func.now())