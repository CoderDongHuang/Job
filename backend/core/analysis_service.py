import asyncio
from typing import Dict, List, Any
from collections import Counter
from database.database import SessionLocal
from models import Job

async def get_salary_analysis() -> Dict[str, Any]:
    """薪资分析"""
    db = SessionLocal()
    try:
        # 查询所有职位
        jobs = db.query(Job).all()
        
        if not jobs:
            return {
                "average_salary": 0,
                "salary_distribution": {},
                "top_paying_cities": [],
                "salary_by_experience": {},
                "total_positions": 0
            }
        
        # 计算平均薪资
        total_salary = sum((job.salary_min + job.salary_max) // 2 for job in jobs)
        average_salary = total_salary // len(jobs) if jobs else 0
        
        # 薪资分布
        salary_ranges = {
            "0-5K": 0,
            "5K-10K": 0,
            "10K-15K": 0,
            "15K-20K": 0,
            "20K-30K": 0,
            "30K+": 0
        }
        
        for job in jobs:
            avg_sal = (job.salary_min + job.salary_max) // 2
            if avg_sal < 5000:
                salary_ranges["0-5K"] += 1
            elif avg_sal < 10000:
                salary_ranges["5K-10K"] += 1
            elif avg_sal < 15000:
                salary_ranges["10K-15K"] += 1
            elif avg_sal < 20000:
                salary_ranges["15K-20K"] += 1
            elif avg_sal < 30000:
                salary_ranges["20K-30K"] += 1
            else:
                salary_ranges["30K+"] += 1
        
        # 高薪城市
        city_salaries = {}
        for job in jobs:
            if job.city not in city_salaries:
                city_salaries[job.city] = []
            city_salaries[job.city].append((job.salary_min + job.salary_max) // 2)
        
        avg_city_salaries = {
            city: sum(sals) // len(sals) for city, sals in city_salaries.items()
        }
        
        top_paying_cities = sorted(
            avg_city_salaries.items(), 
            key=lambda x: x[1], 
            reverse=True
        )[:5]
        
        # 按经验要求的平均薪资
        exp_salaries = {}
        for job in jobs:
            exp = job.experience_required
            if exp not in exp_salaries:
                exp_salaries[exp] = []
            exp_salaries[exp].append((job.salary_min + job.salary_max) // 2)
        
        avg_exp_salaries = {
            exp: sum(sals) // len(sals) for exp, sals in exp_salaries.items()
        }
        
        return {
            "average_salary": average_salary,
            "salary_distribution": salary_ranges,
            "top_paying_cities": [{"city": city, "avg_salary": salary} for city, salary in top_paying_cities],
            "salary_by_experience": avg_exp_salaries,
            "total_positions": len(jobs)
        }
    finally:
        db.close()

async def get_city_analysis() -> Dict[str, Any]:
    """城市分析"""
    db = SessionLocal()
    try:
        jobs = db.query(Job).all()
        
        if not jobs:
            return {
                "city_job_distribution": {},
                "city_average_salary": {},
                "top_job_cities": {}
            }
        
        city_counts = Counter(job.city for job in jobs)
        
        # 计算各城市的平均薪资
        city_salaries = {}
        
        for job in jobs:
            city = job.city
            if city not in city_salaries:
                city_salaries[city] = []
            city_salaries[city].append((job.salary_min + job.salary_max) // 2)
        
        avg_city_salaries = {
            city: sum(sals) // len(sals) for city, sals in city_salaries.items()
        }
        
        return {
            "city_job_distribution": dict(city_counts.most_common(20)),  # 增加到20个城市
            "city_average_salary": avg_city_salaries,
            "top_job_cities": dict(city_counts.most_common(10))  # 仅返回职位数量最多的10个城市
        }
    finally:
        db.close()

async def get_experience_analysis() -> Dict[str, Any]:
    """经验要求分析"""
    db = SessionLocal()
    try:
        jobs = db.query(Job).all()
        
        if not jobs:
            return {
                "experience_distribution": {},
                "average_salary_by_experience": {}
            }
        
        exp_counts = Counter(job.experience_required for job in jobs)
        
        # 按经验要求分组统计薪资
        exp_salary = {}
        for job in jobs:
            exp_req = job.experience_required
            if exp_req not in exp_salary:
                exp_salary[exp_req] = []
            exp_salary[exp_req].append((job.salary_min + job.salary_max) // 2)
        
        avg_exp_salary = {
            exp: sum(sals) // len(sals) for exp, sals in exp_salary.items()
        }
        
        return {
            "experience_distribution": dict(exp_counts),
            "average_salary_by_experience": avg_exp_salary
        }
    finally:
        db.close()

async def get_industry_analysis() -> Dict[str, Any]:
    """行业分析"""
    db = SessionLocal()
    try:
        jobs = db.query(Job).all()
        
        if not jobs:
            return {
                "category_distribution": {},
                "average_salary_by_category": {}
            }
        
        category_counts = Counter(job.category for job in jobs)
        
        # 按行业统计薪资
        category_salaries = {}
        for job in jobs:
            category = job.category
            if category not in category_salaries:
                category_salaries[category] = []
            category_salaries[category].append((job.salary_min + job.salary_max) // 2)
        
        avg_category_salary = {
            cat: sum(sals) // len(sals) for cat, sals in category_salaries.items()
        }
        
        return {
            "category_distribution": dict(category_counts.most_common(20)),  # 增加到20个类别
            "average_salary_by_category": avg_category_salary
        }
    finally:
        db.close()