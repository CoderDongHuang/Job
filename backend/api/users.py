from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import List, Optional
from datetime import timedelta

from schemas.user import (
    UserCreate, UserResponse, UserLogin, Token, 
    UserUpdate, UserProfileUpdate, UserSkillUpdate
)
from core.user_service import (
    create_user, authenticate_user, get_user_by_id,
    update_user_profile, update_user_skills, get_user_recommendations,
    get_demo_users, UserService
)

router = APIRouter(prefix="/users", tags=["users"])
security = HTTPBearer()

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """获取当前用户"""
    token = credentials.credentials
    payload = UserService.verify_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user = await get_user_by_id(int(user_id))
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户不存在",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user

@router.post("/register", response_model=UserResponse)
async def register_user(user_data: UserCreate):
    """用户注册"""
    try:
        user = await create_user(user_data)
        return user
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/login", response_model=Token)
async def login_user(login_data: UserLogin):
    """用户登录"""
    user = await authenticate_user(login_data.username, login_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=30)
    access_token = UserService.create_access_token(
        data={"sub": str(user.id)}, expires_delta=access_token_expires
    )
    
    return Token(
        access_token=access_token,
        token_type="bearer",
        user=user
    )

@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(current_user: UserResponse = Depends(get_current_user)):
    """获取当前用户信息"""
    return current_user

@router.put("/me", response_model=UserResponse)
async def update_current_user_profile(
    profile_data: UserProfileUpdate,
    current_user: UserResponse = Depends(get_current_user)
):
    """更新当前用户信息"""
    updated_user = await update_user_profile(current_user.id, profile_data)
    if not updated_user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    return updated_user

@router.put("/me/skills", response_model=UserResponse)
async def update_current_user_skills(
    skill_data: UserSkillUpdate,
    current_user: UserResponse = Depends(get_current_user)
):
    """更新当前用户技能"""
    updated_user = await update_user_skills(current_user.id, skill_data.skills)
    if not updated_user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    return updated_user

@router.get("/me/recommendations", response_model=dict)
async def get_user_recommendations_endpoint(
    current_user: UserResponse = Depends(get_current_user)
):
    """获取用户个性化推荐"""
    recommendations = await get_user_recommendations(current_user.id)
    return recommendations

@router.get("/demo", response_model=List[UserResponse])
async def get_demo_users_endpoint():
    """获取演示用户数据（无需认证）"""
    return await get_demo_users()

# 管理员功能（可选）
@router.get("/", response_model=List[UserResponse])
async def get_all_users():
    """获取所有用户（管理员功能）"""
    # 这里可以添加管理员权限检查
    return await get_demo_users()  # 暂时返回演示数据

@router.get("/{user_id}", response_model=UserResponse)
async def get_user_by_id_endpoint(user_id: int):
    """根据ID获取用户"""
    user = await get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    return user