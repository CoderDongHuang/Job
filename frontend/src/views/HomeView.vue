<template>
  <div class="home">
    <el-row :gutter="20" class="hero-section">
      <el-col :span="24">
        <h1>智析招聘 - 招聘数据分析与技能洞察系统</h1>
        <p class="subtitle">通过大数据分析为您提供精准的技能趋势分析、薪资预测和职业发展建议</p>
      </el-col>
    </el-row>

    <el-row :gutter="20" class="stats-section">
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-number">10K+</div>
          <div class="stat-label">职位数据</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-number">500+</div>
          <div class="stat-label">技能标签</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-number">300+</div>
          <div class="stat-label">城市覆盖</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-number">95%</div>
          <div class="stat-label">分析准确率</div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" class="features-section">
      <el-col :span="8">
        <el-card class="feature-card">
          <div class="feature-icon">
            <el-icon><Histogram /></el-icon>
          </div>
          <h3>技能趋势分析</h3>
          <p>实时分析市场需求变化，掌握技能发展趋势</p>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card class="feature-card">
          <div class="feature-icon">
            <el-icon><Money /></el-icon>
          </div>
          <h3>薪资预测</h3>
          <p>基于您的技能组合预测市场薪资水平</p>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card class="feature-card">
          <div class="feature-icon">
            <el-icon><User /></el-icon>
          </div>
          <h3>个性化推荐</h3>
          <p>为您定制专属的职业发展路径和学习计划</p>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" class="quick-search">
      <el-col :span="24">
        <el-card>
          <h3>快速职位搜索</h3>
          <el-input
            v-model="searchKeyword"
            placeholder="请输入职位关键词，如：Python、前端、Java..."
            size="large"
            @keyup.enter="performSearch"
          >
            <template #append>
              <el-button icon="Search" @click="performSearch" size="large">搜索</el-button>
            </template>
          </el-input>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { Histogram, Money, User, Search } from '@element-plus/icons-vue'

export default {
  name: 'HomeView',
  setup() {
    const searchKeyword = ref('')
    const router = useRouter()

    const performSearch = () => {
      if (searchKeyword.value.trim()) {
        router.push(`/jobs?keyword=${encodeURIComponent(searchKeyword.value)}`)
      }
    }

    return {
      searchKeyword,
      performSearch,
      Histogram,
      Money,
      User,
      Search
    }
  }
}
</script>

<style scoped>
.hero-section {
  text-align: center;
  margin-bottom: 40px;
  padding: 40px 20px;
  background: linear-gradient(135deg, #74b9ff, #0984e3);
  color: white;
  border-radius: 10px;
}

.hero-section h1 {
  margin: 0 0 15px 0;
  font-size: 2.5em;
}

.subtitle {
  font-size: 1.2em;
  opacity: 0.9;
}

.stats-section {
  margin-bottom: 40px;
}

.stat-card {
  text-align: center;
  padding: 20px;
}

.stat-number {
  font-size: 2em;
  font-weight: bold;
  color: #409EFF;
}

.stat-label {
  margin-top: 10px;
  color: #666;
}

.features-section {
  margin-bottom: 40px;
}

.feature-card {
  text-align: center;
  padding: 30px 20px;
  height: 200px;
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.feature-icon {
  font-size: 2.5em;
  color: #409EFF;
  margin-bottom: 15px;
}

.feature-card h3 {
  margin: 10px 0;
  font-size: 1.3em;
}

.quick-search {
  margin-top: 30px;
}

.quick-search h3 {
  margin-bottom: 20px;
  text-align: center;
}
</style>