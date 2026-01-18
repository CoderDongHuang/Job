from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from urllib.parse import quote_plus

# 数据库URL - 可以通过环境变量配置
# MySQL示例: mysql+pymysql://username:password@localhost:3306/job_analysis
DATABASE_URL = os.getenv("DATABASE_URL", "mysql+pymysql://root:123456@localhost:3306/job_analysis")

# 对密码进行URL编码，以防特殊字符
if "mysql" in DATABASE_URL:
    # 分离URL各部分
    parts = DATABASE_URL.split('@')
    if len(parts) > 1:
        credentials_and_host = parts[0].split('://')[1]
        credentials = credentials_and_host.split(':')[1]  # 获取密码部分
        encoded_credentials = quote_plus(credentials)
        # 重建URL
        protocol = parts[0].split('://')[0] + '://'
        user_part = credentials_and_host.split(':')[0] + ':' + encoded_credentials
        DATABASE_URL = protocol + user_part + '@' + parts[1]

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,  # 测试连接是否仍然有效
    echo=False  # 生产环境中设为False
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()