from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from schemas.job import JobCreate, JobResponse
from core.job_service import (
    create_job, get_jobs, get_job_by_id, 
    search_jobs, delete_job, update_job
)

router = APIRouter(prefix="/jobs", tags=["jobs"])

@router.post("/", response_model=JobResponse)
async def create_job_endpoint(job: JobCreate):
    """创建职位信息"""
    return await create_job(job)

@router.get("/{job_id}", response_model=JobResponse)
async def get_job_endpoint(job_id: int):
    """根据ID获取职位信息"""
    job = await get_job_by_id(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job

@router.get("/", response_model=List[JobResponse])
async def get_jobs_endpoint(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    keyword: Optional[str] = Query(None),
    city: Optional[str] = Query(None),
    salary_min: Optional[int] = Query(None, ge=0),
    salary_max: Optional[int] = Query(None, ge=0),
    experience: Optional[str] = Query(None),
    education: Optional[str] = Query(None),
    category: Optional[str] = Query(None)
):
    """获取职位列表"""
    return await get_jobs(
        skip=skip, 
        limit=limit, 
        keyword=keyword,
        city=city,
        salary_min=salary_min,
        salary_max=salary_max,
        experience=experience,
        education=education,
        category=category
    )

@router.put("/{job_id}", response_model=JobResponse)
async def update_job_endpoint(job_id: int, job: JobCreate):
    """更新职位信息"""
    updated_job = await update_job(job_id, job)
    if not updated_job:
        raise HTTPException(status_code=404, detail="Job not found")
    return updated_job

@router.delete("/{job_id}")
async def delete_job_endpoint(job_id: int):
    """删除职位信息"""
    deleted = await delete_job(job_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Job not found")
    return {"message": "Job deleted successfully"}

@router.get("/search/", response_model=List[JobResponse])
async def search_jobs_endpoint(
    q: str = Query(..., min_length=1),
    city: Optional[str] = Query(None),
    salary_min: Optional[int] = Query(None),
    salary_max: Optional[int] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100)
):
    """搜索职位"""
    return await search_jobs(q, city, salary_min, salary_max, skip, limit)