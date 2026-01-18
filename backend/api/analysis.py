from fastapi import APIRouter
from typing import Dict, Any
from core.analysis_service import (
    get_salary_analysis, get_city_analysis, 
    get_experience_analysis, get_industry_analysis
)
from core.real_time_analysis import get_real_time_analysis

router = APIRouter(prefix="/analysis", tags=["analysis"])

@router.get("/salary")
async def salary_analysis():
    """薪资分析"""
    return await get_salary_analysis()

@router.get("/city")
async def city_analysis():
    """城市分析"""
    return await get_city_analysis()

@router.get("/experience")
async def experience_analysis():
    """经验要求分析"""
    return await get_experience_analysis()

@router.get("/industry")
async def industry_analysis():
    """行业分析"""
    return await get_industry_analysis()

# 为了支持图表数据，我们也可以提供特定格式的数据端点
@router.get("/salary-distribution")
async def salary_distribution():
    """薪资分布数据，专为图表使用"""
    data = await get_salary_analysis()
    distribution = data.get("salary_distribution", {})
    
    # 转换为图表友好的格式
    chart_data = [{"name": k, "value": v} for k, v in distribution.items()]
    
    return {
        "title": "薪资分布",
        "data": chart_data
    }

@router.get("/city-salary-ranking")
async def city_salary_ranking():
    """城市薪资排名，专为图表使用"""
    data = await get_city_analysis()
    avg_salaries = data.get("city_average_salary", {})
    
    # 转换为前端期望的格式
    cities = list(avg_salaries.keys())
    salaries = list(avg_salaries.values())
    
    return {
        "cities": cities,
        "salaries": salaries
    }

@router.get("/experience-distribution")
async def experience_distribution():
    """经验分布数据，专为图表使用"""
    data = await get_experience_analysis()
    distribution = data.get("experience_distribution", {})
    
    # 转换为前端期望的格式
    experiences = list(distribution.keys())
    counts = list(distribution.values())
    
    return {
        "experiences": experiences,
        "counts": counts
    }

@router.get("/industry-salary-ranking")
async def industry_salary_ranking():
    """行业薪资排名，专为图表使用"""
    data = await get_industry_analysis()
    avg_salaries = data.get("average_salary_by_category", {})
    
    # 转换为前端期望的格式
    industries = list(avg_salaries.keys())
    salaries = list(avg_salaries.values())
    
    return {
        "industries": industries,
        "salaries": salaries
    }

@router.get("/real-time")
async def real_time_analysis():
    """实时数据分析"""
    return await get_real_time_analysis()