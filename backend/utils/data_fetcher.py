import requests
import json
import os
import time
from typing import List, Dict, Any
import random

class JobDataFetcher:
    """职位数据获取器"""
    
    def __init__(self):
        self.api_endpoints = {
            'github_jobs': 'https://jobs.github.com/positions.json',
            'remoteok': 'https://remoteok.io/api',
            'mockaroo': f'https://my.api.mockaroo.com/jobs.json?key={os.getenv("MOCKAROO_KEY", "test")}'
        }
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json'
        }
    
    def fetch_from_github_jobs(self, description: str = "", location: str = "") -> List[Dict[str, Any]]:
        """从GitHub Jobs API获取数据"""
        try:
            params = {}
            if description:
                params['description'] = description
            if location:
                params['location'] = location
                
            response = requests.get(self.api_endpoints['github_jobs'], 
                                 params=params, headers=self.headers, timeout=10)
            
            if response.status_code == 200:
                jobs = response.json()
                return self._transform_github_jobs(jobs)
        except Exception as e:
            print(f"GitHub Jobs API请求失败: {e}")
        
        return []
    
    def _transform_github_jobs(self, jobs: List[Dict]) -> List[Dict[str, Any]]:
        """转换GitHub Jobs数据格式"""
        transformed = []
        
        for job in jobs[:10]:  # 限制数量
            transformed_job = {
                'title': job.get('title', ''),
                'company': job.get('company', ''),
                'city': self._extract_city(job.get('location', '')),
                'salary_min': random.randint(3000, 15000),
                'salary_max': random.randint(15000, 40000),
                'experience_required': random.choice(['1-3年', '3-5年', '5-10年']),
                'education_required': random.choice(['本科', '硕士', '不限']),
                'description': job.get('description', '')[:500] if job.get('description') else '职位描述',
                'requirements': '具备相关工作经验和技术能力',
                'category': self._categorize_job(job.get('title', '')),
                'tags': self._extract_tags(job.get('description', '')),
                'created_at': time.strftime('%Y-%m-%d %H:%M:%S'),
                'updated_at': time.strftime('%Y-%m-%d %H:%M:%S')
            }
            transformed.append(transformed_job)
        
        return transformed
    
    def fetch_mock_data(self) -> List[Dict[str, Any]]:
        """获取模拟数据（当API不可用时使用）"""
        # 生成丰富的模拟数据
        job_titles = [
            'Python开发工程师', '前端开发工程师', 'Java开发工程师', '数据分析师',
            '机器学习工程师', '后端开发工程师', '全栈工程师', '移动端开发工程师',
            'DevOps工程师', '测试工程师', '产品经理', 'UI/UX设计师'
        ]
        
        companies = [
            '阿里巴巴', '腾讯', '百度', '字节跳动', '美团', '滴滴', '京东',
            '华为', '小米', '网易', '拼多多', '快手', 'B站', '携程'
        ]
        
        cities = ['北京', '上海', '深圳', '广州', '杭州', '南京', '武汉', '成都', '西安', '厦门']
        
        skills_map = {
            'Python': ['Python', 'Django', 'Flask', '爬虫', '数据分析'],
            '前端': ['JavaScript', 'Vue.js', 'React', 'HTML5', 'CSS3'],
            'Java': ['Java', 'Spring', '微服务', '分布式'],
            '数据': ['Python', 'SQL', '数据分析', '机器学习'],
            '机器学习': ['Python', 'TensorFlow', 'PyTorch', '深度学习'],
            '后端': ['Java', 'Python', 'MySQL', 'Redis'],
            '全栈': ['JavaScript', 'Python', 'Vue.js', 'Node.js'],
            '移动端': ['Android', 'iOS', 'Flutter', 'React Native'],
            'DevOps': ['Docker', 'Kubernetes', 'CI/CD', 'Linux'],
            '测试': ['自动化测试', 'Selenium', '性能测试'],
            '产品': ['产品设计', '需求分析', '项目管理'],
            '设计': ['UI设计', 'UX设计', '原型设计', 'Sketch']
        }
        
        jobs = []
        for i in range(50):  # 生成50个职位
            title = random.choice(job_titles)
            category = next((cat for cat in skills_map.keys() if cat in title), '技术')
            
            job = {
                'title': title,
                'company': random.choice(companies),
                'city': random.choice(cities),
                'salary_min': random.randint(8000, 20000),
                'salary_max': random.randint(20000, 50000),
                'experience_required': random.choice(['应届毕业生', '1年以内', '1-3年', '3-5年', '5-10年']),
                'education_required': random.choice(['大专', '本科', '硕士', '博士']),
                'description': f"{title}职位，负责相关技术开发工作。要求具备扎实的专业知识和良好的团队合作精神。",
                'requirements': f"要求具备{random.choice(['相关专业', '工作经验', '技术能力'])}，熟悉相关技术栈。",
                'category': category,
                'tags': random.sample(skills_map.get(category, ['技术']), min(3, len(skills_map.get(category, ['技术'])))),
                'created_at': time.strftime('%Y-%m-%d %H:%M:%S'),
                'updated_at': time.strftime('%Y-%m-%d %H:%M:%S')
            }
            jobs.append(job)
        
        return jobs
    
    def _extract_city(self, location: str) -> str:
        """从位置字符串中提取城市"""
        chinese_cities = ['北京', '上海', '深圳', '广州', '杭州', '南京', '武汉', '成都', '西安', '厦门']
        for city in chinese_cities:
            if city in location:
                return city
        return random.choice(chinese_cities)
    
    def _categorize_job(self, title: str) -> str:
        """根据职位标题分类"""
        categories = {
            'Python': '后端开发',
            '前端': '前端开发', 
            'Java': '后端开发',
            '数据': '数据分析',
            '机器学习': '人工智能',
            '后端': '后端开发',
            '全栈': '全栈开发',
            '移动端': '移动开发',
            'DevOps': '运维开发',
            '测试': '软件测试',
            '产品': '产品经理',
            '设计': 'UI/UX设计'
        }
        
        for keyword, category in categories.items():
            if keyword in title:
                return category
        return '技术'
    
    def _extract_tags(self, description: str) -> List[str]:
        """从描述中提取技能标签"""
        common_skills = [
            'Python', 'Java', 'JavaScript', 'Vue.js', 'React', 'Node.js',
            'MySQL', 'Redis', 'Docker', 'Kubernetes', 'Linux', 'Git',
            '机器学习', '深度学习', '数据分析', '爬虫', '自动化', '测试'
        ]
        
        found_skills = []
        for skill in common_skills:
            if skill in description:
                found_skills.append(skill)
        
        # 如果没有找到，返回一些通用技能
        if not found_skills:
            found_skills = random.sample(common_skills, min(3, len(common_skills)))
        
        return found_skills


def fetch_job_data(source: str = "mock") -> List[Dict[str, Any]]:
    """获取职位数据的主函数"""
    fetcher = JobDataFetcher()
    
    if source == "github":
        return fetcher.fetch_from_github_jobs()
    elif source == "mock":
        return fetcher.fetch_mock_data()
    else:
        return []