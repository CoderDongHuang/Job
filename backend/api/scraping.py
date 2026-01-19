from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Dict, Any, List
from database.database import SessionLocal
from models import Job
from sqlalchemy import func
from datetime import datetime
from utils.data_fetcher import fetch_job_data

class ScrapingRequest(BaseModel):
    source: str

router = APIRouter(prefix="/scraping", tags=["scraping"])

# 爬取状态跟踪
scraping_status = {
    "is_running": False,
    "last_run": None,
    "job_count": 0,
    "error": None
}

async def scrape_data_task(source: str):
    """后台爬取任务"""
    try:
        scraping_status["is_running"] = True
        scraping_status["error"] = None
        
        if source == "github":
            jobs = fetch_job_data("github")
        elif source == "mock":
            jobs = fetch_job_data("mock")
        elif source == "real":
            jobs = fetch_job_data("real")
        else:
            scraping_status["error"] = f"不支持的数据源: {source}"
            return
        
        # 保存到数据库
        db = SessionLocal()
        try:
            # 统计现有数据
            existing_count = db.query(func.count(Job.id)).scalar()
            
            # 批量插入新数据，智能去重
            new_jobs_count = 0
            for job_data in jobs:
                # 对于模拟数据，使用更宽松的重复检查
                if source == "mock":
                    # 只检查完全相同的记录
                    existing_job = db.query(Job).filter(
                        Job.title == job_data.get('title', ''),
                        Job.company == job_data.get('company', ''),
                        Job.city == job_data.get('city', ''),
                        Job.salary_min == job_data.get('salary_min', 0),
                        Job.salary_max == job_data.get('salary_max', 0)
                    ).first()
                else:
                    # 对于真实数据，使用严格的重复检查
                    existing_job = db.query(Job).filter(
                        Job.title == job_data.get('title', ''),
                        Job.company == job_data.get('company', '')
                    ).first()
                
                if not existing_job:
                    job = Job(**job_data)
                    db.add(job)
                    new_jobs_count += 1
            
            db.commit()
            
            # 更新爬取状态
            scraping_status["job_count"] = new_jobs_count
            scraping_status["last_run"] = datetime.now().isoformat()
            scraping_status["total_jobs"] = existing_count + new_jobs_count
            
        except Exception as e:
            db.rollback()
            scraping_status["error"] = f"数据库错误: {str(e)}"
        finally:
            db.close()
            
    except Exception as e:
        scraping_status["error"] = f"爬取错误: {str(e)}"
    finally:
        scraping_status["is_running"] = False

@router.post("/trigger")
async def trigger_scraping(request_data: ScrapingRequest, background_tasks: BackgroundTasks):
    """触发数据爬取"""
    source = request_data.source
    
    if scraping_status["is_running"]:
        raise HTTPException(status_code=400, detail="爬取任务正在运行中")
    
    if source not in ["github", "mock", "real"]:
        raise HTTPException(status_code=400, detail="不支持的数据源")
    
    # 启动后台任务
    background_tasks.add_task(scrape_data_task, source)
    
    return {
        "message": f"已开始从 {source} 爬取数据",
        "source": source,
        "status": "started"
    }

@router.get("/status")
async def get_scraping_status():
    """获取爬取状态"""
    return {
        "is_running": scraping_status["is_running"],
        "last_run": scraping_status["last_run"],
        "job_count": scraping_status.get("job_count", 0),
        "total_jobs": scraping_status.get("total_jobs", 0),
        "error": scraping_status["error"],
        "current_time": datetime.now().isoformat()
    }

@router.get("/stats")
async def get_scraping_stats():
    """获取爬取统计信息"""
    db = SessionLocal()
    try:
        # 获取数据库统计
        total_jobs = db.query(func.count(Job.id)).scalar()
        
        # 按城市统计
        city_stats = db.query(
            Job.city, 
            func.count(Job.id).label('count'),
            func.avg(Job.salary_min).label('avg_min_salary'),
            func.avg(Job.salary_max).label('avg_max_salary')
        ).group_by(Job.city).all()
        
        # 按类别统计
        category_stats = db.query(
            Job.category, 
            func.count(Job.id).label('count')
        ).group_by(Job.category).all()
        
        return {
            "total_jobs": total_jobs,
            "city_stats": [
                {
                    "city": stat.city,
                    "count": stat.count,
                    "avg_min_salary": float(stat.avg_min_salary or 0),
                    "avg_max_salary": float(stat.avg_max_salary or 0)
                }
                for stat in city_stats
            ],
            "category_stats": [
                {
                    "category": stat.category,
                    "count": stat.count
                }
                for stat in category_stats
            ]
        }
    finally:
        db.close()

@router.delete("/clear")
async def clear_all_jobs():
    """清空所有职位数据"""
    if scraping_status["is_running"]:
        raise HTTPException(status_code=400, detail="爬取任务正在运行中，无法清空数据")
    
    db = SessionLocal()
    try:
        # 删除所有数据
        deleted_count = db.query(Job).delete()
        db.commit()
        
        # 重置统计
        scraping_status["total_jobs"] = 0
        scraping_status["job_count"] = 0
        
        return {
            "message": f"已清空 {deleted_count} 条职位数据",
            "deleted_count": deleted_count
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"清空数据失败: {str(e)}")
    finally:
        db.close()