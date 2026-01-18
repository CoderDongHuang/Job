"""
数据库初始化脚本
用于首次运行时初始化数据库并填充真实数据
"""
import sys
import os

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.database.database import Base
from backend.database.database import engine as db_engine
from backend.core.job_service import create_job
from backend.models import Job
from backend.utils.data_fetcher import fetch_job_data
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_db_with_real_data():
    """使用真实数据初始化数据库"""
    logger.info("开始初始化数据库...")
    
    # 从database模块导入engine
    from backend.database.database import engine
    
    # 创建所有表
    Base.metadata.create_all(bind=engine)
    logger.info("数据库表创建完成")
    
    # 获取真实数据
    logger.info("正在获取真实职位数据...")
    jobs_data = fetch_job_data("mock")
    
    if not jobs_data:
        logger.warning("未能获取到真实数据，数据库将为空")
        return
    
    logger.info(f"获取到 {len(jobs_data)} 条职位数据，开始插入数据库...")
    
    # 插入数据到数据库
    from backend.database.database import SessionLocal
    db = SessionLocal()
    try:
        for job_data in jobs_data:
            # 检查是否已存在相同标题和公司的职位
            existing_job = db.query(Job).filter(
                Job.title == job_data['title'],
                Job.company == job_data['company']
            ).first()
            
            if not existing_job:
                job = Job(
                    title=job_data['title'],
                    company=job_data['company'],
                    city=job_data['city'],
                    salary_min=job_data['salary_min'],
                    salary_max=job_data['salary_max'],
                    experience_required=job_data['experience_required'],
                    education_required=job_data['education_required'],
                    description=job_data['description'],
                    requirements=job_data['requirements'],
                    category=job_data['category'],
                    tags=job_data['tags']  # SQLAlchemy会自动处理JSON字段
                )
                db.add(job)
        
        db.commit()
        logger.info(f"成功插入 {len(jobs_data)} 条职位数据到数据库")
    except Exception as e:
        logger.error(f"插入数据时出错: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    init_db_with_real_data()