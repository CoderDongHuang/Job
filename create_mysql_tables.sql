-- 创建数据库
CREATE DATABASE IF NOT EXISTS job_analysis CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- 使用数据库
USE job_analysis;

-- 创建职位表
CREATE TABLE jobs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL COMMENT '职位名称',
    company VARCHAR(255) NOT NULL COMMENT '公司名称',
    city VARCHAR(100) NOT NULL COMMENT '城市',
    salary_min INT NOT NULL COMMENT '最低薪资(元)',
    salary_max INT NOT NULL COMMENT '最高薪资(元)',
    experience_required VARCHAR(50) NOT NULL COMMENT '经验要求',
    education_required VARCHAR(50) NOT NULL COMMENT '学历要求',
    description TEXT COMMENT '职位描述',
    requirements TEXT COMMENT '职位要求',
    category VARCHAR(100) NOT NULL COMMENT '职位类别',
    tags JSON COMMENT '技能标签(json格式)',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    INDEX idx_title (title),
    INDEX idx_company (company),
    INDEX idx_city (city),
    INDEX idx_category (category),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='职位信息表';

-- 创建用户表
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL COMMENT '用户名',
    email VARCHAR(100) UNIQUE NOT NULL COMMENT '邮箱',
    password_hash VARCHAR(255) NOT NULL COMMENT '加密密码',
    full_name VARCHAR(100) COMMENT '姓名',
    title VARCHAR(100) COMMENT '职位标题',
    experience_years INT DEFAULT 0 COMMENT '工作经验年数',
    current_salary INT DEFAULT 0 COMMENT '当前薪资',
    target_salary INT DEFAULT 0 COMMENT '期望薪资',
    location VARCHAR(50) COMMENT '所在城市',
    education VARCHAR(50) COMMENT '学历',
    skills TEXT COMMENT '技能列表(JSON格式)',
    resume TEXT COMMENT '简历内容',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    INDEX idx_username (username),
    INDEX idx_email (email),
    INDEX idx_location (location)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='用户表';

-- 创建技能分析结果表
CREATE TABLE skill_analysis_results (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT COMMENT '用户ID',
    input_text TEXT NOT NULL COMMENT '输入文本',
    extracted_skills JSON COMMENT '提取的技能',
    skill_frequency JSON COMMENT '技能频率',
    related_skills JSON COMMENT '相关技能',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    INDEX idx_user_id (user_id),
    INDEX idx_created_at (created_at),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='技能分析结果表';

-- 创建用户职位收藏表
CREATE TABLE user_job_favorites (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL COMMENT '用户ID',
    job_id INT NOT NULL COMMENT '职位ID',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '收藏时间',
    UNIQUE KEY unique_user_job (user_id, job_id),
    INDEX idx_user_id (user_id),
    INDEX idx_job_id (job_id),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (job_id) REFERENCES jobs(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='用户职位收藏表';

-- 创建用户搜索历史表
CREATE TABLE user_search_history (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL COMMENT '用户ID',
    search_query VARCHAR(255) NOT NULL COMMENT '搜索关键词',
    search_filters JSON COMMENT '搜索筛选条件',
    result_count INT DEFAULT 0 COMMENT '搜索结果数量',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '搜索时间',
    INDEX idx_user_id (user_id),
    INDEX idx_created_at (created_at),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='用户搜索历史表';

-- 创建数据爬取日志表
CREATE TABLE data_scraping_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    source VARCHAR(100) NOT NULL COMMENT '数据源',
    job_count INT DEFAULT 0 COMMENT '爬取职位数量',
    status VARCHAR(20) NOT NULL COMMENT '状态(success/error)',
    error_message TEXT COMMENT '错误信息',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '爬取时间',
    INDEX idx_source (source),
    INDEX idx_status (status),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='数据爬取日志表';