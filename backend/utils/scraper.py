import requests
import pandas as pd
import json
import random
from typing import List, Dict, Any
from urllib.parse import urlparse
from bs4 import BeautifulSoup
import time
import os


def scrape_job_data_from_api() -> List[Dict[str, Any]]:
    """
    从合法API获取职位数据
    注意：在实际应用中，应使用有授权的API
    """
    jobs_data = []
    
    # 首先尝试从环境变量定义的数据源获取
    data_source_url = os.getenv('JOB_DATA_SOURCE_URL', None)
    
    if data_source_url:
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.get(data_source_url, headers=headers)
            if response.status_code == 200:
                jobs_data = response.json()
                print(f"成功从API获取 {len(jobs_data)} 条职位数据")
        except Exception as e:
            print(f"从API获取数据失败: {e}")
    
    return jobs_data


def scrape_job_data_from_csv(csv_path: str) -> List[Dict[str, Any]]:
    """
    从本地CSV文件加载职位数据
    """
    jobs_data = []
    
    if os.path.exists(csv_path):
        try:
            df = pd.read_csv(csv_path)
            # 转换DataFrame为字典列表
            jobs_data = df.to_dict('records')
            # 将numpy类型转换为原生Python类型
            for job in jobs_data:
                for key, value in job.items():
                    if pd.isna(value):
                        job[key] = None
                    elif hasattr(value, 'dtype'):
                        if pd.api.types.is_integer_dtype(value):
                            job[key] = int(value)
                        elif pd.api.types.is_float_dtype(value):
                            job[key] = float(value)
            print(f"成功从CSV文件加载 {len(jobs_data)} 条职位数据")
        except Exception as e:
            print(f"从CSV文件读取数据失败: {e}")
    
    return jobs_data


def scrape_job_data_from_json(json_path: str) -> List[Dict[str, Any]]:
    """
    从本地JSON文件加载职位数据
    """
    jobs_data = []
    
    if os.path.exists(json_path):
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                jobs_data = json.load(f)
            print(f"成功从JSON文件加载 {len(jobs_data)} 条职位数据")
        except Exception as e:
            print(f"从JSON文件读取数据失败: {e}")
    
    return jobs_data


def scrape_job_data_from_public_datasets() -> List[Dict[str, Any]]:
    """
    从公共数据集获取示例职位数据（用于演示目的）
    在实际应用中，这应该被替换为真实的职位数据源
    """
    jobs_data = []
    
    # 示例：使用公开的测试API获取数据并转换为职位格式
    # 这仅用于演示，实际应用中应使用合法的职位数据源
    try:
        # 获取一些示例数据作为基础
        posts_url = "https://jsonplaceholder.typicode.com/posts"
        response = requests.get(posts_url)
        if response.status_code == 200:
            posts = response.json()[:20]  # 限制为前20条
            
            cities = ["北京", "上海", "深圳", "广州", "杭州", "南京", "武汉", "成都", "西安", "厦门"]
            experiences = ["应届毕业生", "1年以内", "1-3年", "3-5年", "5-10年", "10年以上"]
            educations = ["不限", "大专", "本科", "硕士", "博士"]
            categories = ["技术", "产品", "设计", "运营", "市场", "职能"]
            
            for i, post in enumerate(posts):
                job_entry = {
                    'title': f"{random.choice(categories)}工程师" if i % 2 == 0 else f"{random.choice(categories)}专员",
                    'company': f"示例公司 {i % 5 + 1}",
                    'city': random.choice(cities),
                    'salary_min': random.randint(6000, 15000),
                    'salary_max': random.randint(18000, 50000),
                    'experience_required': random.choice(experiences),
                    'education_required': random.choice(educations),
                    'description': post['body'][:200] + "...",
                    'requirements': f"要求：{random.choice(educations)}及以上学历，{random.choice(experiences)}经验",
                    'category': random.choice(categories),
                    'tags': ["技术", "互联网", "计算机"]  # 这里可以进一步分析描述提取标签
                }
                jobs_data.append(job_entry)
                
    except Exception as e:
        print(f"从公共数据集获取数据失败: {e}")
    
    return jobs_data


def fetch_job_listings() -> List[Dict[str, Any]]:
    """
    主要的数据获取函数，整合多种数据源
    """
    all_jobs = []
    
    # 1. 尝试从API获取数据
    api_data = scrape_job_data_from_api()
    all_jobs.extend(api_data)
    
    if not all_jobs:
        # 2. 尝试从本地CSV文件获取数据
        csv_path = os.path.join(os.path.dirname(__file__), '..', '..', 'job_data.csv')
        csv_data = scrape_job_data_from_csv(csv_path)
        all_jobs.extend(csv_data)
    
    if not all_jobs:
        # 3. 尝试从本地JSON文件获取数据
        json_path = os.path.join(os.path.dirname(__file__), '..', '..', 'job_data.json')
        json_data = scrape_job_data_from_json(json_path)
        all_jobs.extend(json_data)
    
    if not all_jobs:
        # 4. 最后，从公共数据集获取示例数据
        public_data = scrape_job_data_from_public_datasets()
        all_jobs.extend(public_data)
    
    # 数据清洗和标准化
    cleaned_jobs = []
    for job in all_jobs:
        cleaned_job = {
            'title': str(job.get('title', job.get('job_title', job.get('position', '未知')))),
            'company': str(job.get('company', job.get('company_name', job.get('employer', '未知公司')))),
            'city': str(job.get('city', job.get('location', job.get('workplace_address', '远程')))),
            'salary_min': int(job.get('salary_min', job.get('min_salary', 0))),
            'salary_max': int(job.get('salary_max', job.get('max_salary', 0))),
            'experience_required': str(job.get('experience_required', job.get('experience', job.get('required_experience', '不限')))),
            'education_required': str(job.get('education_required', job.get('education', job.get('required_education', '不限')))),
            'description': str(job.get('description', job.get('job_description', job.get('description_html', '')))),
            'requirements': str(job.get('requirements', job.get('requirement', job.get('job_requirements', '')))),
            'category': str(job.get('category', job.get('job_category', job.get('position_category', '技术')))),
            'tags': job.get('tags', job.get('skills', job.get('required_skills', [])))
        }
        
        # 确保tags是列表格式
        if isinstance(cleaned_job['tags'], str):
            try:
                cleaned_job['tags'] = json.loads(cleaned_job['tags'])
            except:
                cleaned_job['tags'] = [tag.strip() for tag in cleaned_job['tags'].split(',') if tag.strip()]
        
        cleaned_jobs.append(cleaned_job)
    
    print(f"总共获取并处理了 {len(cleaned_jobs)} 条职位数据")
    return cleaned_jobs