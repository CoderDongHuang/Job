import re
from typing import List, Dict, Any

def clean_salary_text(salary_str: str) -> tuple:
    """
    清理薪资文本，提取最低和最高薪资
    示例: "8千-1.5万/月" -> (8000, 15000)
    """
    if not salary_str:
        return 0, 0
    
    # 统一转换为小写并移除非必要字符
    cleaned = re.sub(r'[^\d.-万千万千]', '', salary_str.lower())
    
    # 匹配薪资范围，例如 "8千-1.5万" 或 "10000-20000"
    match = re.search(r'([\d.]+)([万千千])?-([\d.]+)([万千千])?', cleaned)
    
    if match:
        min_val = float(match.group(1))
        max_val = float(match.group(3))
        
        # 处理单位
        min_unit = match.group(2) if match.group(2) else ''
        max_unit = match.group(4) if match.group(4) else ''
        
        # 转换单位
        if '千' in min_unit or 'k' in min_unit:
            min_val *= 1000
        elif '万' in min_unit:
            min_val *= 10000
            
        if '千' in max_unit or 'k' in max_unit:
            max_val *= 1000
        elif '万' in max_unit:
            max_val *= 10000
    
        return int(min_val), int(max_val)
    
    # 如果没有匹配到范围，尝试匹配单个值
    single_match = re.search(r'([\d.]+)([万千千])?', cleaned)
    if single_match:
        val = float(single_match.group(1))
        unit = single_match.group(2) if single_match.group(2) else ''
        
        if '千' in unit or 'k' in unit:
            val *= 1000
        elif '万' in unit:
            val *= 10000
            
        return int(val), int(val)
    
    return 0, 0

def extract_location_info(location_str: str) -> Dict[str, str]:
    """
    从位置字符串中提取城市和区域信息
    示例: "上海市浦东新区" -> {"city": "上海", "district": "浦东新区"}
    """
    if not location_str:
        return {"city": "", "district": ""}
    
    # 简单的位置解析逻辑
    if '市' in location_str:
        city_end = location_str.find('市') + 1
        city = location_str[:city_end]
        
        district_start = city_end
        if district_start < len(location_str):
            district = location_str[district_start:]
            if '区' in district or '县' in district or '镇' in district:
                # 提取第一个区/县/镇
                for sep in ['区', '县', '镇']:
                    idx = district.find(sep)
                    if idx != -1:
                        district = district[:idx+1]
                        break
        else:
            district = ""
    else:
        city = location_str.split()[0] if location_str.split() else ""
        district = ""
    
    return {
        "city": city.replace('市', ''),
        "district": district
    }

def normalize_job_title(title: str) -> str:
    """
    标准化职位标题
    """
    if not title:
        return ""
    
    # 移除多余的空格和特殊字符
    title = re.sub(r'\s+', ' ', title.strip())
    
    # 统一大小写
    title = title.lower().title()
    
    return title

def extract_tags_from_description(description: str) -> List[str]:
    """
    从职位描述中提取潜在的技能标签
    这是一个改进版本，使用更通用的方法从描述中提取关键词
    """
    if not description:
        return []
    
    description_lower = description.lower()
    
    # 更通用的技能关键词提取
    # 使用更广泛的编程语言和技术栈关键词
    tech_keywords = [
        # 编程语言
        'python', 'java', 'javascript', 'typescript', 'go', 'rust', 'c++', 'c#', 'php', 'ruby',
        'swift', 'kotlin', 'scala', 'r', 'matlab', 'sql', 'shell', 'bash',
        
        # Web技术
        'react', 'vue', 'angular', 'html', 'css', 'sass', 'less', 'node.js', 'express',
        'django', 'flask', 'spring', 'mybatis', 'laravel', 'rails',
        
        # 数据库
        'mysql', 'postgresql', 'mongodb', 'redis', 'oracle', 'sqlserver', 'sqlite',
        
        # 云平台和DevOps
        'docker', 'kubernetes', 'aws', 'azure', 'gcp', 'jenkins', 'git', 'linux', 'nginx',
        
        # 数据科学和AI
        'tensorflow', 'pytorch', 'machine learning', 'deep learning', 'ai', 'nlp', 'cv',
        'pandas', 'numpy', 'scikit-learn', 'jupyter', 'matplotlib',
        
        # 其他技能
        'restful', 'api', 'microservices', 'agile', 'scrum', 'ci/cd', 'devops'
    ]
    
    extracted_tags = set()
    for keyword in tech_keywords:
        if keyword in description_lower:
            # 标准化关键词格式
            normalized_tag = keyword.replace('.', '').replace('/', '').replace(' ', '').lower()
            extracted_tags.add(normalized_tag.title())
    
    # 也可以从描述中提取其他类型的标签，如工作性质、经验要求等
    common_tags = [
        'remote', 'onsite', 'hybrid', 'fulltime', 'parttime',
        'internship', 'senior', 'junior', 'lead', 'manager',
        'startup', 'enterprise', 'fintech', 'healthcare', 'ecommerce'
    ]
    
    for tag in common_tags:
        if tag in description_lower:
            extracted_tags.add(tag.title())
    
    return list(extracted_tags)

def parse_job_data_from_raw(raw_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    从原始数据中解析职位信息，标准化数据格式
    """
    # 解析薪资
    salary_text = raw_data.get('salary', raw_data.get('salary_range', ''))
    if salary_text and isinstance(salary_text, str):
        salary_min, salary_max = clean_salary_text(salary_text)
    else:
        salary_min = raw_data.get('salary_min', 0)
        salary_max = raw_data.get('salary_max', 0)
    
    # 解析位置
    location_text = raw_data.get('location', raw_data.get('workplace_address', raw_data.get('address', '')))
    location_info = extract_location_info(location_text)
    
    # 提取技能标签
    description = raw_data.get('description', raw_data.get('job_description', ''))
    requirements = raw_data.get('requirements', raw_data.get('requirement', ''))
    
    # 合并描述和要求来提取技能
    combined_desc = f"{description} {requirements}".lower()
    extracted_tags = extract_tags_from_description(combined_desc)
    
    # 如果原始数据中有标签，也合并进来
    if 'tags' in raw_data and raw_data['tags']:
        if isinstance(raw_data['tags'], list):
            extracted_tags.extend(raw_data['tags'])
        elif isinstance(raw_data['tags'], str):
            # 如果是字符串，按逗号分割
            extracted_tags.extend([tag.strip().title() for tag in raw_data['tags'].split(',')])
    
    # 标准化职位标题
    title = raw_data.get('title', raw_data.get('job_title', raw_data.get('position', '')))
    normalized_title = normalize_job_title(title)
    
    # 确保标签唯一且非空
    unique_tags = list(set(filter(lambda x: x.strip() != '', extracted_tags)))
    
    return {
        'title': normalized_title,
        'company': raw_data.get('company', raw_data.get('company_name', raw_data.get('employer', ''))),
        'city': location_info['city'],
        'district': location_info['district'],
        'salary_min': salary_min,
        'salary_max': salary_max,
        'experience_required': raw_data.get('experience_required', raw_data.get('experience', raw_data.get('required_experience', ''))),
        'education_required': raw_data.get('education_required', raw_data.get('education', raw_data.get('required_education', ''))),
        'description': description,
        'requirements': requirements,
        'category': raw_data.get('category', raw_data.get('job_category', raw_data.get('position_category', '技术'))),
        'tags': unique_tags
    }