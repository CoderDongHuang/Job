from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List
import json

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

class JobUpdate(BaseModel):
    title: Optional[str] = None
    company: Optional[str] = None
    city: Optional[str] = None
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    experience_required: Optional[str] = None
    education_required: Optional[str] = None
    description: Optional[str] = None
    requirements: Optional[str] = None
    category: Optional[str] = None
    tags: Optional[List[str]] = None

class JobResponse(JobBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True
    
    @classmethod
    def model_validate(cls, obj):
        """自定义验证方法以处理JSON字段"""
        # 创建基础实例
        instance_data = {
            'id': obj.id,
            'title': obj.title,
            'company': obj.company,
            'city': obj.city,
            'salary_min': obj.salary_min,
            'salary_max': obj.salary_max,
            'experience_required': obj.experience_required,
            'education_required': obj.education_required,
            'description': obj.description,
            'requirements': obj.requirements,
            'category': obj.category,
            'created_at': obj.created_at,
            'updated_at': obj.updated_at
        }
        
        # 处理tags字段 - 从JSON字符串转换为列表
        if obj.tags:
            if isinstance(obj.tags, str):
                try:
                    instance_data['tags'] = json.loads(obj.tags)
                except json.JSONDecodeError:
                    instance_data['tags'] = []
            elif isinstance(obj.tags, list):
                instance_data['tags'] = obj.tags
            else:
                instance_data['tags'] = []
        else:
            instance_data['tags'] = []
        
        return cls(**instance_data)