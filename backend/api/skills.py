from fastapi import APIRouter, HTTPException
from typing import List
from backend.schemas.skill import SkillAnalysisRequest, SkillAnalysisResponse
from backend.core.skill_analyzer import analyze_skills, get_skill_trends, extract_skills_from_text, get_skill_recommendations

router = APIRouter(prefix="/skills", tags=["skills"])

@router.post("/analyze", response_model=SkillAnalysisResponse)
async def analyze_skills_endpoint(request: SkillAnalysisRequest):
    """分析技能需求"""
    return await analyze_skills(request)

@router.get("/trends", response_model=dict)
async def get_skill_trends_endpoint():
    """获取技能趋势"""
    return await get_skill_trends()

@router.post("/extract", response_model=dict)
async def extract_skills_endpoint(text: dict):
    """从文本中提取技能"""
    if "text" not in text:
        raise HTTPException(status_code=400, detail="Text field is required")
    extracted_skills = await extract_skills_from_text(text["text"])
    return {"skills": extracted_skills}

@router.get("/top-skills", response_model=dict)
async def get_top_skills_endpoint(limit: int = 10):
    """获取热门技能列表"""
    trends_data = await get_skill_trends()
    return {
        "rising_skills": trends_data.get("rising_skills", [])[:limit],
        "total_skills_analyzed": trends_data.get("total_skills_analyzed", 0),
        "unique_skills": trends_data.get("unique_skills", 0)
    }

@router.post("/recommendations", response_model=dict)
async def get_skill_recommendations_endpoint(skills: dict):
    """获取技能推荐"""
    if "skills" not in skills:
        raise HTTPException(status_code=400, detail="Skills field is required")
    
    user_skills = skills["skills"]
    if not isinstance(user_skills, list):
        raise HTTPException(status_code=400, detail="Skills should be a list")
    
    return await get_skill_recommendations(user_skills)