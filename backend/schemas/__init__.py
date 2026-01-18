from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List, Dict

class JobBase(BaseModel):
    title: str
    company: str
    city: str
    salary_min: int
    salary_max: int
    experience_required: str
    education_required: str
    description: str
    requirements: str
    category: str
    tags: Optional[List[str]] = []

class JobCreate(JobBase):
    pass

class JobUpdate(JobBase):
    pass

class JobResponse(JobBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class SkillAnalysisRequest(BaseModel):
    text: str
    top_k: Optional[int] = 10

class SkillAnalysisResponse(BaseModel):
    extracted_skills: List[str]
    skill_frequency: Dict[str, int]
    related_skills: Dict[str, List[str]]
    
class UserBase(BaseModel):
    username: str
    email: str
    full_name: Optional[str] = None

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[str] = None
    full_name: Optional[str] = None

class UserResponse(UserBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True