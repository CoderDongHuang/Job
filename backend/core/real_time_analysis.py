"""
实时数据分析服务
基于当前数据库中的职位数据进行实时分析
"""
import asyncio
from typing import Dict, List, Any
from collections import Counter
from database.database import SessionLocal
from models import Job

async def get_real_time_analysis() -> Dict[str, Any]:
    """获取实时数据分析结果"""
    db = SessionLocal()
    try:
        # 查询所有职位数据
        jobs = db.query(Job).all()
        
        if not jobs:
            return {
                "total_jobs": 0,
                "cities": [],
                "salaries": [],
                "experiences": [],
                "counts": [],
                "industries": [],
                "industry_salaries": [],
                "skills": [],
                "skill_counts": []
            }
        
        # 1. 城市薪资分析
        city_salaries = {}
        for job in jobs:
            if job.city not in city_salaries:
                city_salaries[job.city] = []
            city_salaries[job.city].append((job.salary_min + job.salary_max) // 2)
        
        # 计算各城市平均薪资并排序
        avg_city_salaries = {}
        for city, salaries in city_salaries.items():
            if salaries:
                avg_city_salaries[city] = sum(salaries) // len(salaries)
        
        # 按薪资排序，取前10个城市
        sorted_cities = sorted(avg_city_salaries.items(), key=lambda x: x[1], reverse=True)[:10]
        cities = [city for city, _ in sorted_cities]
        salaries = [salary for _, salary in sorted_cities]
        
        # 2. 经验要求分布
        exp_counts = Counter(job.experience_required for job in jobs)
        experiences = list(exp_counts.keys())
        counts = list(exp_counts.values())
        
        # 3. 行业薪资分析
        industry_salaries = {}
        for job in jobs:
            if job.category not in industry_salaries:
                industry_salaries[job.category] = []
            industry_salaries[job.category].append((job.salary_min + job.salary_max) // 2)
        
        avg_industry_salaries = {}
        for industry, salaries in industry_salaries.items():
            if salaries:
                avg_industry_salaries[industry] = sum(salaries) // len(salaries)
        
        # 按薪资排序，取前10个行业
        sorted_industries = sorted(avg_industry_salaries.items(), key=lambda x: x[1], reverse=True)[:10]
        industries = [industry for industry, _ in sorted_industries]
        industry_salaries_list = [salary for _, salary in sorted_industries]
        
        # 4. 技能热度分析（从职位标签中提取）
        all_skills = []
        for job in jobs:
            if job.tags:
                try:
                    import json
                    skills = json.loads(job.tags) if isinstance(job.tags, str) else job.tags
                    if isinstance(skills, list):
                        all_skills.extend(skills)
                except:
                    pass
        
        skill_counts = Counter(all_skills)
        # 取前10个热门技能
        top_skills = skill_counts.most_common(10)
        skills = [skill for skill, _ in top_skills]
        skill_counts_list = [count for _, count in top_skills]
        
        return {
            "total_jobs": len(jobs),
            "cities": cities,
            "salaries": salaries,
            "experiences": experiences,
            "counts": counts,
            "industries": industries,
            "industry_salaries": industry_salaries_list,
            "skills": skills,
            "skill_counts": skill_counts_list
        }
        
    finally:
        db.close()