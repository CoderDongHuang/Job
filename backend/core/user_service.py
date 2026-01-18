import bcrypt
import jwt
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from models.user import User
from schemas.user import UserCreate, UserUpdate, UserResponse, UserLogin
from database.database import SessionLocal
import json
import os

# JWT配置
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

class UserService:
    """用户服务类"""
    
    @staticmethod
    def hash_password(password: str) -> str:
        """加密密码"""
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """验证密码"""
        return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))
    
    @staticmethod
    def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
        """创建JWT token"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
    
    @staticmethod
    def verify_token(token: str) -> Optional[Dict[str, Any]]:
        """验证JWT token"""
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            return payload
        except jwt.PyJWTError:
            return None

async def create_user(user_data: UserCreate) -> UserResponse:
    """创建用户"""
    db = SessionLocal()
    try:
        # 检查用户名和邮箱是否已存在
        existing_user = db.query(User).filter(
            (User.username == user_data.username) | (User.email == user_data.email)
        ).first()
        
        if existing_user:
            raise ValueError("用户名或邮箱已存在")
        
        # 创建用户
        user_dict = user_data.dict()
        password = user_dict.pop('password')
        user_dict['password_hash'] = UserService.hash_password(password)
        
        # 处理技能列表
        if 'skills' in user_dict:
            if user_dict['skills']:
                user_dict['skills'] = json.dumps(user_dict['skills'], ensure_ascii=False)
            else:
                user_dict['skills'] = None
        
        db_user = User(**user_dict)
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        
        return UserResponse.model_validate(db_user)
    finally:
        db.close()

def calculate_salary_by_skills(user_skills: list, user_experience: int, user_location: str) -> tuple:
    """基于技能和经验计算薪资范围（备选算法）"""
    # 技能权重和薪资影响因子
    skill_weights = {
        'Python': {'weight': 0.8, 'salary_boost': 0.15},
        'Java': {'weight': 0.7, 'salary_boost': 0.12},
        'JavaScript': {'weight': 0.8, 'salary_boost': 0.13},
        'TypeScript': {'weight': 0.6, 'salary_boost': 0.10},
        'Vue.js': {'weight': 0.7, 'salary_boost': 0.08},
        'React': {'weight': 0.8, 'salary_boost': 0.12},
        'MySQL': {'weight': 0.6, 'salary_boost': 0.05},
        'Redis': {'weight': 0.5, 'salary_boost': 0.04},
        'Docker': {'weight': 0.7, 'salary_boost': 0.10},
        'Kubernetes': {'weight': 0.8, 'salary_boost': 0.15},
        '机器学习': {'weight': 0.9, 'salary_boost': 0.20},
        '数据分析': {'weight': 0.7, 'salary_boost': 0.12},
        '前端开发': {'weight': 0.6, 'salary_boost': 0.08},
        '后端开发': {'weight': 0.7, 'salary_boost': 0.10},
        'DevOps': {'weight': 0.8, 'salary_boost': 0.15}
    }
    
    # 计算用户技能总分
    user_skill_score = sum(skill_weights.get(skill, {'weight': 0.5})['weight'] for skill in user_skills)
    
    # 基于技能和经验的薪资基准
    base_salary = 8000  # 应届生基准薪资
    experience_multiplier = 1 + (user_experience * 0.1)  # 每年经验增加10%
    skill_multiplier = 1 + (user_skill_score * 0.05)  # 技能总分每分增加5%
    
    # 计算合理的薪资范围
    reasonable_min = int(base_salary * experience_multiplier * skill_multiplier * 0.8)
    reasonable_max = int(base_salary * experience_multiplier * skill_multiplier * 1.3)
    
    # 城市薪资系数
    city_multipliers = {
        '北京': 1.3, '上海': 1.3, '深圳': 1.25, '广州': 1.15,
        '杭州': 1.2, '成都': 1.1, '南京': 1.1, '武汉': 1.05
    }
    city_multiplier = city_multipliers.get(user_location, 1.0)
    reasonable_min = int(reasonable_min * city_multiplier)
    reasonable_max = int(reasonable_max * city_multiplier)
    
    return reasonable_min, reasonable_max

def generate_job_recommendations_from_db(user_skills: list, user_location: str, user_experience: int, max_salary: int) -> list:
    """基于数据库中的真实职位数据生成推荐"""
    from database.database import SessionLocal
    from models import Job
    from sqlalchemy import or_
    
    db = SessionLocal()
    try:
        # 构建技能匹配查询
        query = db.query(Job)
        
        # 技能匹配条件
        if user_skills:
            skill_conditions = []
            for skill in user_skills:
                skill_conditions.append(Job.description.contains(skill))
                skill_conditions.append(Job.requirements.contains(skill))
            
            if skill_conditions:
                query = query.filter(or_(*skill_conditions))
        
        # 城市匹配
        if user_location:
            query = query.filter(Job.city == user_location)
        
        # 薪资范围筛选
        query = query.filter(Job.salary_max <= max_salary * 1.5)  # 允许稍高薪资
        
        # 获取匹配的职位
        matched_jobs = query.limit(5).all()
        
        # 转换为推荐格式
        recommendations = []
        for job in matched_jobs:
            # 计算匹配度
            match_score = calculate_job_match_score(job, user_skills, user_experience)
            
            # 提取匹配的技能
            matched_skills = []
            for skill in user_skills:
                if skill in job.description or skill in job.requirements:
                    matched_skills.append(skill)
            
            # 提取缺失的技能
            all_skills = extract_skills_from_text(job.requirements)
            missing_skills = [skill for skill in all_skills if skill not in user_skills]
            
            recommendations.append({
                'id': job.id,
                'title': job.title,
                'company': job.company,
                'city': job.city,
                'salary_min': job.salary_min,
                'salary_max': job.salary_max,
                'experience_required': job.experience_required or '经验不限',
                'match_score': match_score,
                'matched_skills': matched_skills[:3],
                'missing_skills': missing_skills[:3]
            })
        
        # 按匹配度排序
        recommendations.sort(key=lambda x: x['match_score'], reverse=True)
        
        # 如果没有足够匹配的职位，补充一些热门职位
        if len(recommendations) < 3:
            popular_jobs = db.query(Job).filter(Job.city == user_location).order_by(Job.salary_max.desc()).limit(3).all()
            for job in popular_jobs:
                if job.id not in [r['id'] for r in recommendations]:
                    recommendations.append({
                        'id': job.id,
                        'title': job.title,
                        'company': job.company,
                        'city': job.city,
                        'salary_min': job.salary_min,
                        'salary_max': job.salary_max,
                        'experience_required': job.experience_required or '经验不限',
                        'match_score': 50,  # 默认匹配度
                        'matched_skills': [],
                        'missing_skills': extract_skills_from_text(job.requirements)[:3]
                    })
        
        return recommendations
    
    finally:
        db.close()

def calculate_job_match_score(job, user_skills: list, user_experience: int) -> int:
    """计算职位匹配度"""
    score = 0
    
    # 技能匹配度（60%）
    if user_skills:
        job_skills = extract_skills_from_text(job.requirements)
        matched_count = sum(1 for skill in user_skills if skill in job_skills)
        skill_score = min(60, matched_count * 10)
        score += skill_score
    
    # 经验匹配度（20%）
    if job.experience_required:
        exp_score = calculate_experience_match(user_experience, job.experience_required)
        score += exp_score
    
    # 城市匹配度（20%）
    if job.city:
        score += 20  # 城市匹配基础分
    
    return min(100, score)

def calculate_experience_match(user_experience: int, required_experience: str) -> int:
    """计算经验匹配度"""
    # 解析经验要求（如："1-3年", "3年以上"等）
    import re
    
    # 匹配数字模式
    numbers = re.findall(r'\d+', required_experience)
    if numbers:
        if len(numbers) == 2:
            min_exp, max_exp = map(int, numbers)
            if min_exp <= user_experience <= max_exp:
                return 20  # 完全匹配
            elif user_experience > max_exp:
                return 15  # 经验超出
            else:
                return max(0, 20 - (min_exp - user_experience) * 5)  # 经验不足
        else:
            exp_required = int(numbers[0])
            if '以上' in required_experience:
                if user_experience >= exp_required:
                    return 20
                else:
                    return max(0, 20 - (exp_required - user_experience) * 5)
    
    return 10  # 默认分数

def extract_skills_from_text(text: str) -> list:
    """从文本中提取技能关键词"""
    if not text:
        return []
    
    # 技能关键词列表
    skill_keywords = [
        'Python', 'Java', 'JavaScript', 'TypeScript', 'Vue.js', 'React',
        'MySQL', 'Redis', 'Docker', 'Kubernetes', 'Git', 'Linux',
        '机器学习', '数据分析', '前端开发', '后端开发', 'DevOps',
        'HTML5', 'CSS3', 'Node.js', 'Spring', 'Django', 'Flask',
        'MongoDB', 'PostgreSQL', 'Nginx', 'Apache', 'TensorFlow',
        'PyTorch', 'Scikit-learn', 'Pandas', 'NumPy', 'AWS', 'Azure'
    ]
    
    found_skills = []
    for skill in skill_keywords:
        if skill in text:
            found_skills.append(skill)
    
    return found_skills

async def authenticate_user(username: str, password: str) -> Optional[UserResponse]:
    """用户认证"""
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.username == username).first()
        if not user:
            return None
        
        if not UserService.verify_password(password, user.password_hash):
            return None
        
        # 使用to_dict方法确保技能字段是列表类型
        user_dict = user.to_dict()
        return UserResponse(**user_dict)
    finally:
        db.close()

async def get_user_by_id(user_id: int) -> Optional[UserResponse]:
    """根据ID获取用户"""
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if user:
            # 使用to_dict方法确保技能字段是列表类型
            user_dict = user.to_dict()
            return UserResponse(**user_dict)
        return None
    finally:
        db.close()

async def update_user_profile(user_id: int, user_data: UserUpdate) -> Optional[UserResponse]:
    """更新用户信息"""
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return None
        
        # 更新字段
        for field, value in user_data.dict(exclude_unset=True).items():
            if field == 'skills' and value is not None:
                # 处理技能列表
                setattr(user, field, json.dumps(value, ensure_ascii=False))
            else:
                setattr(user, field, value)
        
        db.commit()
        db.refresh(user)
        
        # 使用to_dict方法确保技能字段是列表类型
        user_dict = user.to_dict()
        return UserResponse(**user_dict)
    finally:
        db.close()

async def update_user_skills(user_id: int, skills: list) -> Optional[UserResponse]:
    """更新用户技能"""
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return None
        
        user.set_skills(skills)
        db.commit()
        db.refresh(user)
        
        # 创建用户响应对象，确保技能字段是列表类型
        user_dict = user.to_dict()
        return UserResponse(**user_dict)
    finally:
        db.close()

async def get_user_recommendations(user_id: int) -> Dict[str, Any]:
    """获取用户个性化推荐 - 基于用户技能进行精确匹配"""
    user = await get_user_by_id(user_id)
    if not user:
        return {}
    
    # 获取用户信息
    user_skills = user.skills or []
    user_location = user.location
    user_experience = user.experience_years or 0
    current_salary = user.current_salary or 0
    target_salary = user.target_salary or 0
    user_title = user.title or ""
    
    # 基于数据库中的真实职位数据进行薪资评估
    from database.database import SessionLocal
    from models import Job
    from sqlalchemy import func, and_, or_
    
    db = SessionLocal()
    try:
        # 1. 基于用户技能匹配相关职位
        skill_query = db.query(Job)
        if user_skills:
            # 构建技能查询条件
            skill_conditions = []
            for skill in user_skills:
                skill_conditions.append(Job.description.contains(skill))
                skill_conditions.append(Job.requirements.contains(skill))
            
            if skill_conditions:
                skill_query = skill_query.filter(or_(*skill_conditions))
        
        # 2. 基于用户所在城市筛选
        if user_location:
            skill_query = skill_query.filter(Job.city == user_location)
        
        # 3. 基于用户经验筛选合适的职位
        experience_filtered_jobs = skill_query.all()
        
        # 4. 计算匹配职位的薪资统计数据
        if experience_filtered_jobs:
            # 计算平均薪资
            avg_min = sum(job.salary_min for job in experience_filtered_jobs) / len(experience_filtered_jobs)
            avg_max = sum(job.salary_max for job in experience_filtered_jobs) / len(experience_filtered_jobs)
            
            # 根据用户经验调整薪资范围
            experience_factor = min(1.0 + (user_experience * 0.15), 2.5)  # 最多2.5倍
            reasonable_min = int(avg_min * experience_factor * 0.8)  # 80%作为下限
            reasonable_max = int(avg_max * experience_factor * 1.2)  # 120%作为上限
        else:
            # 如果没有匹配职位，使用基于技能和经验的算法
            reasonable_min, reasonable_max = calculate_salary_by_skills(user_skills, user_experience, user_location)
    
    finally:
        db.close()
    
    # 基于用户技能生成职位推荐（使用真实数据库数据）
    recommended_jobs = generate_job_recommendations_from_db(user_skills, user_location, user_experience, reasonable_max)
    
    # 技能缺口分析
    skill_gap_analysis = analyze_skill_gaps(user_skills, user_title)
    
    return {
        "recommended_jobs": recommended_jobs,
        "skill_gap_analysis": skill_gap_analysis,
        "salary_analysis": {
            "reasonable_min": reasonable_min,
            "reasonable_max": reasonable_max,
            "current_salary": current_salary,
            "target_salary": target_salary,
            "salary_gap": target_salary - current_salary if current_salary > 0 else 0
        }
    }

def generate_job_recommendations(user_skills: list, user_location: str, max_salary: int) -> list:
    """基于用户技能生成职位推荐"""
    
    # 职位数据库（根据技能匹配）
    job_database = [
        {
            'id': 1,
            'title': 'Python后端开发工程师',
            'company': '阿里巴巴',
            'city': '北京',
            'required_skills': ['Python', 'Django', 'MySQL', 'Redis'],
            'salary_min': 15000,
            'salary_max': 30000,
            'experience_required': '3-5年'
        },
        {
            'id': 2,
            'title': '前端开发工程师',
            'company': '腾讯',
            'city': '深圳',
            'required_skills': ['JavaScript', 'Vue.js', 'React', 'TypeScript'],
            'salary_min': 12000,
            'salary_max': 25000,
            'experience_required': '2-4年'
        },
        {
            'id': 3,
            'title': '全栈开发工程师',
            'company': '字节跳动',
            'city': '北京',
            'required_skills': ['Python', 'JavaScript', 'Vue.js', 'MySQL'],
            'salary_min': 18000,
            'salary_max': 35000,
            'experience_required': '3-5年'
        },
        {
            'id': 4,
            'title': '数据科学家',
            'company': '百度',
            'city': '北京',
            'required_skills': ['Python', '机器学习', '数据分析', 'TensorFlow'],
            'salary_min': 20000,
            'salary_max': 40000,
            'experience_required': '3-5年'
        },
        {
            'id': 5,
            'title': 'DevOps工程师',
            'company': '华为',
            'city': '深圳',
            'required_skills': ['Docker', 'Kubernetes', 'Linux', 'CI/CD'],
            'salary_min': 16000,
            'salary_max': 32000,
            'experience_required': '3-5年'
        }
    ]
    
    # 过滤和排序职位
    filtered_jobs = []
    for job in job_database:
        # 计算技能匹配度
        required_skills = job['required_skills']
        matched_skills = [skill for skill in required_skills if skill in user_skills]
        match_score = int((len(matched_skills) / len(required_skills)) * 100) if required_skills else 0
        
        # 地理位置匹配
        location_match = 1.0 if job['city'] == user_location else 0.7
        
        # 薪资合理性检查
        salary_reasonable = 1.0 if job['salary_max'] <= max_salary * 1.2 else 0.5
        
        # 综合匹配度
        overall_match = int(match_score * 0.6 + location_match * 0.2 + salary_reasonable * 0.2)
        
        if overall_match >= 30:  # 匹配度阈值
            filtered_jobs.append({
                **job,
                'match_score': overall_match,
                'matched_skills': matched_skills,
                'missing_skills': [skill for skill in required_skills if skill not in user_skills]
            })
    
    # 按匹配度排序
    filtered_jobs.sort(key=lambda x: x['match_score'], reverse=True)
    return filtered_jobs[:5]  # 返回前5个推荐

def analyze_skill_gaps(user_skills: list, user_title: str) -> dict:
    """分析技能缺口"""
    
    # 不同职位的核心技能要求
    role_skill_requirements = {
        '前端开发': ['JavaScript', 'HTML5', 'CSS3', 'Vue.js', 'React'],
        '后端开发': ['Python', 'Java', 'MySQL', 'Redis', 'Docker'],
        '全栈开发': ['JavaScript', 'Python', 'Vue.js', 'MySQL', 'Docker'],
        '数据科学': ['Python', '机器学习', '数据分析', 'Pandas', 'SQL'],
        'DevOps': ['Docker', 'Kubernetes', 'Linux', 'CI/CD', '监控']
    }
    
    # 根据用户当前职位或技能推断目标职位
    target_role = infer_target_role(user_skills, user_title)
    required_skills = role_skill_requirements.get(target_role, [])
    
    # 计算技能缺口
    missing_skills = [skill for skill in required_skills if skill not in user_skills]
    
    # 学习路径建议
    learning_path = generate_learning_path(user_skills, missing_skills, target_role)
    
    # 薪资提升预估
    salary_increase = len(missing_skills) * 2000  # 每掌握一个核心技能提升2000元
    
    return {
        "target_role": target_role,
        "missing_skills": missing_skills,
        "suggested_learning_path": learning_path,
        "estimated_salary_increase": salary_increase
    }

def infer_target_role(user_skills: list, user_title: str) -> str:
    """根据技能和职位推断目标职位"""
    role_keywords = {
        '前端开发': ['前端', 'JavaScript', 'Vue', 'React', 'HTML', 'CSS'],
        '后端开发': ['后端', 'Python', 'Java', 'MySQL', '数据库'],
        '全栈开发': ['全栈', '前端', '后端', 'JavaScript', 'Python'],
        '数据科学': ['数据', '分析', '机器学习', 'Python', '统计'],
        'DevOps': ['运维', '部署', 'Docker', 'Kubernetes', 'CI/CD']
    }
    
    # 根据职位标题推断
    if user_title:
        for role, keywords in role_keywords.items():
            if any(keyword in user_title for keyword in keywords):
                return role
    
    # 根据技能推断
    skill_scores = {}
    for role, keywords in role_keywords.items():
        score = sum(1 for keyword in keywords if any(keyword in skill for skill in user_skills))
        skill_scores[role] = score
    
    return max(skill_scores, key=skill_scores.get) if skill_scores else '全栈开发'

def generate_learning_path(current_skills: list, missing_skills: list, target_role: str) -> str:
    """生成学习路径"""
    
    learning_paths = {
        '前端开发': '基础HTML/CSS → JavaScript → Vue.js/React → 工程化工具',
        '后端开发': 'Python/Java基础 → 框架学习 → 数据库 → 部署运维',
        '全栈开发': '前端基础 → 后端基础 → 前后端联调 → 项目实战',
        '数据科学': 'Python基础 → 数据分析 → 机器学习 → 深度学习',
        'DevOps': 'Linux基础 → 容器技术 → 编排工具 → 自动化部署'
    }
    
    base_path = learning_paths.get(target_role, '基础编程 → 项目实践 → 进阶学习')
    
    if missing_skills:
        specific_skills = ' → '.join(missing_skills[:3])
        return f"当前技能 → {specific_skills} → {target_role}精通"
    
    return base_path

async def get_demo_users() -> list:
    """获取演示用户数据"""
    db = SessionLocal()
    try:
        users = db.query(User).limit(5).all()
        return [UserResponse.model_validate(user) for user in users]
    finally:
        db.close()