from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.api import router as api_router
from backend.core.job_service import initialize_job_data
import asyncio
import uvicorn

app = FastAPI(
    title="智析招聘 - 招聘数据分析与技能洞察系统",
    description="通过分析招聘数据，为求职者提供技能趋势分析、薪资预测和职业发展建议",
    version="1.0.0"
)

# CORS设置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 在生产环境中应限制为具体的域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(api_router, prefix="/api/v1")

@app.on_event("startup")
async def startup_event():
    # 初始化职位数据
    print("正在初始化职位数据...")
    count = await initialize_job_data()
    print(f"职位数据初始化完成，共 {count} 条数据")

@app.get("/")
def read_root():
    return {"message": "智析招聘API服务运行正常"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)