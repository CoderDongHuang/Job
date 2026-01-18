from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

class UserBase(BaseModel):
    username: str
    email: EmailStr
    full_name: Optional[str] = None
    title: Optional[str] = None
    experience_years: Optional[int] = 0
    current_salary: Optional[int] = 0
    target_salary: Optional[int] = 0
    location: Optional[str] = None
    education: Optional[str] = None
    skills: Optional[List[str]] = []
    resume: Optional[str] = None

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    title: Optional[str] = None
    experience_years: Optional[int] = None
    current_salary: Optional[int] = None
    target_salary: Optional[int] = None
    location: Optional[str] = None
    education: Optional[str] = None
    skills: Optional[List[str]] = None
    resume: Optional[str] = None

class UserResponse(UserBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class UserLogin(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse

class UserProfileUpdate(BaseModel):
    full_name: Optional[str] = None
    title: Optional[str] = None
    experience_years: Optional[int] = None
    current_salary: Optional[int] = None
    target_salary: Optional[int] = None
    location: Optional[str] = None
    education: Optional[str] = None
    skills: Optional[List[str]] = None
    resume: Optional[str] = None

class UserSkillUpdate(BaseModel):
    skills: List[str]