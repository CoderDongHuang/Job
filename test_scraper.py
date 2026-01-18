from backend.utils.scraper import fetch_job_listings

# 测试爬虫功能
print("开始测试爬虫功能...")
jobs = fetch_job_listings()

print(f"获取到 {len(jobs)} 条职位数据")
if jobs:
    print("前3条数据预览:")
    for i, job in enumerate(jobs[:3]):
        print(f"{i+1}. {job['title']} - {job['company']} - {job['city']} - {job['salary_min']}~{job['salary_max']}")
else:
    print("未能获取到任何数据")