from pydantic import BaseModel
from typing import List, Dict, Optional

class SkillAnalysisRequest(BaseModel):
    text: str
    top_k: Optional[int] = 10

class SkillAnalysisResponse(BaseModel):
    extracted_skills: List[str]
    skill_frequency: Dict[str, int]
    related_skills: Dict[str, List[str]]
    confidence_scores: Dict[str, float]

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

class JobResponse(JobBase):
    id: int
    
    class Config:
        from_attributes = True

class UserBase(BaseModel):
    username: str
    email: str
    full_name: Optional[str] = None

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: int
    
    class Config:
        from_attributes = True