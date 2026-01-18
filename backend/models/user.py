from sqlalchemy import Column, Integer, String, DateTime, Text, JSON
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import json

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(100), nullable=True)
    title = Column(String(100), nullable=True)  # 职位标题，如"前端开发工程师"
    experience_years = Column(Integer, default=0)  # 工作经验年数
    current_salary = Column(Integer, default=0)  # 当前薪资
    target_salary = Column(Integer, default=0)  # 期望薪资
    location = Column(String(50), nullable=True)  # 所在城市
    education = Column(String(50), nullable=True)  # 学历
    skills = Column(Text, nullable=True)  # 技能列表，存储为JSON字符串
    resume = Column(Text, nullable=True)  # 简历内容
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def set_skills(self, skills_list):
        """设置技能列表"""
        if skills_list:
            self.skills = json.dumps(skills_list, ensure_ascii=False)
        else:
            self.skills = None
    
    def get_skills(self):
        """获取技能列表"""
        if self.skills:
            try:
                return json.loads(self.skills)
            except:
                return []
        return []
    
    def to_dict(self):
        """转换为字典格式"""
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "full_name": self.full_name,
            "title": self.title,
            "experience_years": self.experience_years,
            "current_salary": self.current_salary,
            "target_salary": self.target_salary,
            "location": self.location,
            "education": self.education,
            "skills": self.get_skills(),
            "resume": self.resume,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }