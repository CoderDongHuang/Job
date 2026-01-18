from fastapi import APIRouter
from backend.api import jobs, skills, analysis, users, scraping

router = APIRouter()

# 挂载各个模块的路由
router.include_router(jobs.router, tags=["jobs"])
router.include_router(skills.router, tags=["skills"])
router.include_router(analysis.router, tags=["analysis"])
router.include_router(users.router, tags=["users"])
router.include_router(scraping.router, tags=["scraping"])