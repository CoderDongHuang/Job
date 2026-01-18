import asyncio
import re
from typing import List, Dict, Tuple, Any
from collections import Counter, defaultdict
from backend.schemas.skill import SkillAnalysisRequest, SkillAnalysisResponse

# 技能词典 - 这里是部分常用技能，实际项目中可以从外部加载
SKILL_DICTIONARY = {
    "programming_languages": [
        "Python", "Java", "JavaScript", "TypeScript", "C++", "C#", "Go", "Rust", 
        "PHP", "Ruby", "Swift", "Kotlin", "Scala", "R", "MATLAB", "SQL", "NoSQL"
    ],
    "web_frameworks": [
        "React", "Vue", "Angular", "Node.js", "Express", "Django", "Flask", 
        "Spring", "Spring Boot", "Laravel", "Rails", "ASP.NET", "Next.js", "Nuxt.js"
    ],
    "databases": [
        "MySQL", "PostgreSQL", "MongoDB", "Redis", "Oracle", "SQLite", 
        "Elasticsearch", "Cassandra", "MariaDB"
    ],
    "cloud_platforms": [
        "AWS", "Azure", "Google Cloud", "阿里云", "腾讯云", "华为云"
    ],
    "devops_tools": [
        "Docker", "Kubernetes", "Jenkins", "Git", "GitHub", "GitLab", 
        "CI/CD", "Terraform", "Ansible", "Prometheus", "Grafana"
    ],
    "data_science": [
        "TensorFlow", "PyTorch", "Pandas", "NumPy", "Scikit-learn", 
        "Spark", "Hadoop", "Airflow", "Kafka"
    ],
    "mobile_development": [
        "Android", "iOS", "Flutter", "React Native", "Xamarin"
    ],
    "soft_skills": [
        "沟通能力", "团队合作", "问题解决", "项目管理", "领导力", 
        "时间管理", "学习能力", "创新思维"
    ]
}

# 合并所有技能到一个列表
ALL_SKILLS = []
for category, skills in SKILL_DICTIONARY.items():
    ALL_SKILLS.extend(skills)

# 创建技能别名字典
SKILL_ALIASES = {
    "Python3": "Python",
    "Python 3": "Python",
    "JS": "JavaScript",
    "ES6": "JavaScript",
    "Node": "Node.js",
    "ML": "Machine Learning",
    "AI": "Artificial Intelligence",
    "DL": "Deep Learning",
    "ReactJS": "React",
    "VueJS": "Vue",
    "AngularJS": "Angular",
    "SpringBoot": "Spring Boot",
    "Springboot": "Spring Boot",
    "K8s": "Kubernetes",
    "PyTorch": "Pytorch",
    "Tensorflow": "TensorFlow",
    "Postgres": "PostgreSQL",
    "Postgre": "PostgreSQL",
    "MySql": "MySQL",
    "Mysql": "MySQL"
}

async def analyze_skills(request: SkillAnalysisRequest) -> SkillAnalysisResponse:
    """分析文本中的技能"""
    text = request.text.lower()
    top_k = request.top_k
    
    # 提取技能
    extracted_skills = extract_skills_from_text(text)
    
    # 计算技能频率
    skill_freq = Counter(extracted_skills)
    
    # 获取最常见的技能
    most_common_skills = skill_freq.most_common(top_k)
    
    # 计算相关技能（共现分析）
    related_skills = compute_related_skills(extracted_skills)
    
    # 计算置信度分数
    confidence_scores = {skill: freq / len(extracted_skills) for skill, freq in skill_freq.items()}
    
    return SkillAnalysisResponse(
        extracted_skills=list(set(extracted_skills)),
        skill_frequency=dict(skill_freq),
        related_skills=related_skills,
        confidence_scores=confidence_scores
    )

def extract_skills_from_text(text: str) -> List[str]:
    """从文本中提取技能"""
    extracted_skills = []
    
    # 预处理文本
    processed_text = preprocess_text(text)
    
    # 首先尝试精确匹配较长的技能名称
    for skill in ALL_SKILLS:
        # 检查技能名称是否出现在文本中
        if skill.lower() in processed_text:
            extracted_skills.append(skill)
        
        # 检查别名
        for alias, canonical in SKILL_ALIASES.items():
            if alias.lower() in processed_text and canonical not in extracted_skills:
                extracted_skills.append(canonical)
    
    # 使用正则表达式匹配技能模式
    skill_patterns = [
        r'(?:熟悉|精通|掌握|了解|熟练).*?(?:Python|Java|JavaScript|React|Vue|MySQL|Docker|Kubernetes)',
        r'(?:具备|拥有).*?(?:经验|能力|技能)',
        r'(?:熟悉|精通).*?(?:框架|语言|工具|平台)'
    ]
    
    for pattern in skill_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        for match in matches:
            # 从匹配的文本中提取具体的技能
            for skill in ALL_SKILLS:
                if skill.lower() in match.lower() and skill not in extracted_skills:
                    extracted_skills.append(skill)
    
    return extracted_skills

def preprocess_text(text: str) -> str:
    """预处理文本"""
    # 转换为小写
    text = text.lower()
    
    # 移除标点符号
    text = re.sub(r'[^\w\s]', ' ', text)
    
    # 移除多余空格
    text = re.sub(r'\s+', ' ', text)
    
    return text.strip()

def compute_related_skills(skills: List[str]) -> Dict[str, List[str]]:
    """计算相关技能（基于技能分类）"""
    related_skills = {}
    
    for skill in skills:
        related = []
        
        # 找到技能所属的类别
        for category, category_skills in SKILL_DICTIONARY.items():
            if skill in category_skills:
                # 添加同类别下的其他技能
                related.extend([s for s in category_skills if s != skill])
        
        # 添加一些通用的相关技能
        if skill in ["Python", "Java", "JavaScript"]:
            related.extend(["Git", "Docker", "Linux"])
        elif skill in ["React", "Vue", "Angular"]:
            related.extend(["JavaScript", "TypeScript", "HTML", "CSS"])
        elif skill in ["MySQL", "PostgreSQL", "MongoDB"]:
            related.extend(["SQL", "数据库设计", "性能优化"])
        elif skill in ["Docker", "Kubernetes"]:
            related.extend(["CI/CD", "DevOps", "Linux"])
        
        related_skills[skill] = list(set(related))[:5]  # 限制为前5个相关技能
    
    return related_skills

async def get_skill_trends() -> Dict[str, Any]:
    """获取技能趋势数据"""
    # 这里可以连接到真实的数据源，目前返回模拟数据
    return {
        "rising_skills": [
            {"skill": "Python", "growth": 25, "demand": 85},
            {"skill": "Docker", "growth": 22, "demand": 78},
            {"skill": "Kubernetes", "growth": 20, "demand": 72},
            {"skill": "React", "growth": 18, "demand": 80},
            {"skill": "TypeScript", "growth": 15, "demand": 65}
        ],
        "declining_skills": [
            {"skill": "jQuery", "growth": -10, "demand": 30},
            {"skill": "PHP", "growth": -5, "demand": 45},
            {"skill": "AngularJS", "growth": -8, "demand": 25},
            {"skill": "Flash", "growth": -15, "demand": 5},
            {"skill": "VB.NET", "growth": -12, "demand": 20}
        ],
        "hot_categories": [
            {"category": "人工智能", "demand": 90},
            {"category": "云计算", "demand": 85},
            {"category": "前端开发", "demand": 80},
            {"category": "数据科学", "demand": 75},
            {"category": "移动开发", "demand": 70}
        ]
    }

async def get_skill_recommendations(user_skills: List[str]) -> Dict[str, Any]:
    """根据用户技能推荐学习路径"""
    recommendations = []
    
    # 技能分类映射
    skill_categories = {}
    for category, skills in SKILL_DICTIONARY.items():
        for skill in skills:
            skill_categories[skill] = category
    
    # 分析用户技能分布
    user_categories = defaultdict(list)
    for skill in user_skills:
        if skill in skill_categories:
            user_categories[skill_categories[skill]].append(skill)
    
    # 推荐缺失的重要技能
    important_skills = {
        "programming_languages": ["Python", "JavaScript"],
        "web_frameworks": ["React", "Vue"],
        "databases": ["MySQL", "Redis"],
        "devops_tools": ["Git", "Docker"],
        "cloud_platforms": ["AWS", "阿里云"]
    }
    
    for category, important in important_skills.items():
        for skill in important:
            if skill not in user_skills:
                recommendations.append({
                    "skill": skill,
                    "category": category,
                    "reason": f"{skill}是{category}领域的重要技能",
                    "priority": "高"
                })
    
    # 推荐相关技能
    for skill in user_skills:
        related = compute_related_skills([skill]).get(skill, [])
        for related_skill in related[:3]:  # 每个技能推荐3个相关技能
            if related_skill not in user_skills:
                recommendations.append({
                    "skill": related_skill,
                    "category": skill_categories.get(related_skill, "其他"),
                    "reason": f"与{skill}相关的技能",
                    "priority": "中"
                })
    
    return {
        "recommendations": recommendations[:10],  # 限制为前10个推荐
        "skill_gap_analysis": {
            "total_skills": len(user_skills),
            "coverage_percentage": min(100, len(user_skills) * 5),  # 模拟覆盖率
            "missing_categories": [cat for cat in important_skills.keys() if cat not in user_categories]
        }
    }