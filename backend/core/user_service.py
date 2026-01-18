import bcrypt
import jwt
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from backend.models.user import User
from backend.schemas.user import UserCreate, UserUpdate, UserResponse, UserLogin
from backend.database.database import SessionLocal
import json
import os

# JWT配置
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

class UserService:
    """用户服务类"""
    
    @staticmethod
    def hash_password(password: str) -> str:
        """加密密码"""
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """验证密码"""
        return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))
    
    @staticmethod
    def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
        """创建JWT token"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
    
    @staticmethod
    def verify_token(token: str) -> Optional[Dict[str, Any]]:
        """验证JWT token"""
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            return payload
        except jwt.PyJWTError:
            return None

async def create_user(user_data: UserCreate) -> UserResponse:
    """创建用户"""
    db = SessionLocal()
    try:
        # 检查用户名和邮箱是否已存在
        existing_user = db.query(User).filter(
            (User.username == user_data.username) | (User.email == user_data.email)
        ).first()
        
        if existing_user:
            raise ValueError("用户名或邮箱已存在")
        
        # 创建用户
        user_dict = user_data.dict()
        password = user_dict.pop('password')
        user_dict['password_hash'] = UserService.hash_password(password)
        
        # 处理技能列表
        if 'skills' in user_dict:
            if user_dict['skills']:
                user_dict['skills'] = json.dumps(user_dict['skills'], ensure_ascii=False)
            else:
                user_dict['skills'] = None
        
        db_user = User(**user_dict)
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        
        return UserResponse.model_validate(db_user)
    finally:
        db.close()

async def authenticate_user(username: str, password: str) -> Optional[UserResponse]:
    """用户认证"""
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.username == username).first()
        if not user:
            return None
        
        if not UserService.verify_password(password, user.password_hash):
            return None
        
        # 使用to_dict方法确保技能字段是列表类型
        user_dict = user.to_dict()
        return UserResponse(**user_dict)
    finally:
        db.close()

async def get_user_by_id(user_id: int) -> Optional[UserResponse]:
    """根据ID获取用户"""
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if user:
            # 使用to_dict方法确保技能字段是列表类型
            user_dict = user.to_dict()
            return UserResponse(**user_dict)
        return None
    finally:
        db.close()

async def update_user_profile(user_id: int, user_data: UserUpdate) -> Optional[UserResponse]:
    """更新用户信息"""
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return None
        
        # 更新字段
        for field, value in user_data.dict(exclude_unset=True).items():
            if field == 'skills' and value is not None:
                # 处理技能列表
                setattr(user, field, json.dumps(value, ensure_ascii=False))
            else:
                setattr(user, field, value)
        
        db.commit()
        db.refresh(user)
        
        # 使用to_dict方法确保技能字段是列表类型
        user_dict = user.to_dict()
        return UserResponse(**user_dict)
    finally:
        db.close()

async def update_user_skills(user_id: int, skills: list) -> Optional[UserResponse]:
    """更新用户技能"""
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return None
        
        user.set_skills(skills)
        db.commit()
        db.refresh(user)
        
        # 创建用户响应对象，确保技能字段是列表类型
        user_dict = user.to_dict()
        return UserResponse(**user_dict)
    finally:
        db.close()

async def get_user_recommendations(user_id: int) -> Dict[str, Any]:
    """获取用户个性化推荐"""
    user = await get_user_by_id(user_id)
    if not user:
        return {}
    
    # 基于用户技能和偏好生成推荐
    user_skills = user.skills or []
    user_location = user.location
    target_salary = user.target_salary or 0
    
    # 这里可以调用职位推荐算法
    # 暂时返回模拟数据
    return {
        "recommended_jobs": [
            {
                "id": 1,
                "title": "高级前端开发工程师",
                "company": "阿里巴巴",
                "city": user_location or "北京",
                "salary_min": target_salary - 5000,
                "salary_max": target_salary + 5000,
                "match_score": 85
            },
            {
                "id": 2,
                "title": "全栈开发工程师",
                "company": "腾讯",
                "city": user_location or "深圳",
                "salary_min": target_salary - 3000,
                "salary_max": target_salary + 7000,
                "match_score": 78
            }
        ],
        "skill_gap_analysis": {
            "missing_skills": ["TypeScript", "Node.js"],
            "suggested_learning_path": "前端开发 → 全栈开发",
            "estimated_salary_increase": 5000
        }
    }

async def get_demo_users() -> list:
    """获取演示用户数据"""
    db = SessionLocal()
    try:
        users = db.query(User).limit(5).all()
        return [UserResponse.model_validate(user) for user in users]
    finally:
        db.close()