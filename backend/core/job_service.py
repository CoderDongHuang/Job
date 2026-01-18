import asyncio
import json
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func
from backend.models import Job
from backend.schemas.job import JobCreate, JobUpdate, JobResponse
from backend.database.database import SessionLocal
from backend.utils.data_fetcher import fetch_job_data

async def create_job(job_data: JobCreate) -> JobResponse:
    """创建职位"""
    db = SessionLocal()
    try:
        # 将Pydantic模型转换为数据库模型，将tags转换为JSON字符串
        job_dict = job_data.dict()
        if 'tags' in job_dict and isinstance(job_dict['tags'], list):
            job_dict['tags'] = json.dumps(job_dict['tags'], ensure_ascii=False)
        
        db_job = Job(**job_dict)
        db.add(db_job)
        db.commit()
        db.refresh(db_job)
        
        # 转换为响应模型
        return JobResponse.model_validate(db_job)
    finally:
        db.close()

async def get_job_by_id(job_id: int) -> Optional[JobResponse]:
    """根据ID获取职位"""
    from backend.database.database import SessionLocal
    db = SessionLocal()
    try:
        db_job = db.query(Job).filter(Job.id == job_id).first()
        if db_job:
            return JobResponse.model_validate(db_job)
        return None
    finally:
        db.close()

async def get_jobs(
    skip: int = 0, 
    limit: int = 10, 
    keyword: Optional[str] = None,
    city: Optional[str] = None,
    salary_min: Optional[int] = None,
    salary_max: Optional[int] = None,
    experience: Optional[str] = None,
    education: Optional[str] = None,
    category: Optional[str] = None
) -> List[JobResponse]:
    """获取职位列表"""
    from backend.database.database import SessionLocal
    db = SessionLocal()
    try:
        query = db.query(Job)
        
        # 关键词搜索
        if keyword:
            query = query.filter(
                Job.title.contains(keyword) | 
                Job.company.contains(keyword) |
                Job.description.contains(keyword)
            )
        
        # 城市筛选
        if city:
            query = query.filter(Job.city == city)
        
        # 薪资范围筛选
        if salary_min is not None:
            query = query.filter(Job.salary_max >= salary_min)
        if salary_max is not None:
            query = query.filter(Job.salary_min <= salary_max)
        
        # 经验要求筛选
        if experience:
            query = query.filter(Job.experience_required == experience)
        
        # 学历要求筛选
        if education:
            query = query.filter(Job.education_required == education)
        
        # 职位类别筛选
        if category:
            query = query.filter(Job.category == category)
        
        db_jobs = query.offset(skip).limit(limit).all()
        return [JobResponse.model_validate(job) for job in db_jobs]
    finally:
        db.close()

async def update_job(job_id: int, job_data: JobUpdate) -> Optional[JobResponse]:
    """更新职位信息"""
    from backend.database.database import SessionLocal
    db = SessionLocal()
    try:
        db_job = db.query(Job).filter(Job.id == job_id).first()
        if not db_job:
            return None
        
        # 更新字段
        for field, value in job_data.dict(exclude_unset=True).items():
            setattr(db_job, field, value)
        
        db.commit()
        db.refresh(db_job)
        
        return JobResponse.model_validate(db_job)
    finally:
        db.close()

async def delete_job(job_id: int) -> bool:
    """删除职位"""
    from backend.database.database import SessionLocal
    db = SessionLocal()
    try:
        db_job = db.query(Job).filter(Job.id == job_id).first()
        if not db_job:
            return False
        
        db.delete(db_job)
        db.commit()
        return True
    finally:
        db.close()


async def initialize_job_data() -> int:
    """初始化职位数据"""
    from backend.database.database import SessionLocal
    db = SessionLocal()
    try:
        # 检查是否已有数据
        existing_count = db.query(Job).count()
        if existing_count > 0:
            print(f"数据库中已有 {existing_count} 条职位数据，跳过初始化")
            return existing_count
        
        # 获取模拟数据
        jobs_data = fetch_job_data("mock")
        created_count = 0
        
        for job_data in jobs_data:
            try:
                # 创建职位记录
                job_dict = job_data.copy()
                if 'tags' in job_dict and isinstance(job_dict['tags'], list):
                    job_dict['tags'] = json.dumps(job_dict['tags'], ensure_ascii=False)
                
                db_job = Job(**job_dict)
                db.add(db_job)
                created_count += 1
            except Exception as e:
                print(f"创建职位失败: {e}")
        
        db.commit()
        print(f"成功初始化 {created_count} 条职位数据")
        return created_count
        
    except Exception as e:
        print(f"初始化数据失败: {e}")
        db.rollback()
        return 0
    finally:
        db.close()


async def get_job_statistics() -> Dict[str, Any]:
    """获取职位统计信息"""
    from backend.database.database import SessionLocal
    db = SessionLocal()
    try:
        # 总职位数
        total_jobs = db.query(Job).count()
        
        # 按城市统计
        city_stats = db.query(Job.city, func.count(Job.id)).group_by(Job.city).all()
        
        # 按类别统计
        category_stats = db.query(Job.category, func.count(Job.id)).group_by(Job.category).all()
        
        # 平均薪资
        avg_salary_min = db.query(func.avg(Job.salary_min)).scalar() or 0
        avg_salary_max = db.query(func.avg(Job.salary_max)).scalar() or 0
        
        # 热门技能标签
        all_tags = []
        for job in db.query(Job.tags).all():
            if job.tags:
                try:
                    tags = json.loads(job.tags)
                    all_tags.extend(tags)
                except:
                    pass
        
        from collections import Counter
        top_skills = Counter(all_tags).most_common(10)
        
        return {
            'total_jobs': total_jobs,
            'city_distribution': dict(city_stats),
            'category_distribution': dict(category_stats),
            'avg_salary_min': round(avg_salary_min, 2),
            'avg_salary_max': round(avg_salary_max, 2),
            'top_skills': [{'skill': skill, 'count': count} for skill, count in top_skills]
        }
    finally:
        db.close()

async def search_jobs(
    q: str, 
    city: Optional[str] = None, 
    salary_min: Optional[int] = None, 
    salary_max: Optional[int] = None,
    skip: int = 0, 
    limit: int = 10
) -> List[JobResponse]:
    """搜索职位"""
    from backend.database.database import SessionLocal
    db = SessionLocal()
    try:
        query = db.query(Job)
        
        # 根据关键词搜索
        query = query.filter(
            Job.title.contains(q) | 
            Job.company.contains(q) |
            Job.description.contains(q) |
            Job.requirements.contains(q)
        )
        
        # 过滤城市
        if city:
            query = query.filter(Job.city == city)
        
        # 过滤薪资范围
        if salary_min:
            query = query.filter(Job.salary_min >= salary_min)
        if salary_max:
            query = query.filter(Job.salary_max <= salary_max)
        
        db_jobs = query.offset(skip).limit(limit).all()
        return [JobResponse.model_validate(job) for job in db_jobs]
    finally:
        db.close()