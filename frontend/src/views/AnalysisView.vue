<template>
  <div class="analysis-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>数据分析</span>
          <el-button type="primary" @click="refreshAnalysis" :loading="refreshing">
            <el-icon><Refresh /></el-icon>
            刷新数据
          </el-button>
        </div>
      </template>
      
      <!-- 顶部统计信息 -->
      <el-row :gutter="20" style="margin-bottom: 20px;">
        <el-col :span="6">
          <el-statistic title="总职位数" :value="stats.totalJobs || 0" />
        </el-col>
        <el-col :span="6">
          <el-statistic title="平均薪资" :value="stats.avgSalary || 0" suffix="元/月" />
        </el-col>
        <el-col :span="6">
          <el-statistic title="热门城市" :value="stats.topCity ? 1 : 0" :formatter="formatCity" />
        </el-col>
        <el-col :span="6">
          <el-statistic title="热门技能" :value="stats.topSkill ? 1 : 0" :formatter="formatSkill" />
        </el-col>
      </el-row>
      
      <!-- 图表区域 -->
      <el-row :gutter="20">
        <el-col :span="12">
          <el-card>
            <template #header>
              <div class="card-header">
                <span>城市平均薪资对比</span>
              </div>
            </template>
            <div id="city-chart" style="height: 300px;"></div>
          </el-card>
        </el-col>
        
        <el-col :span="12">
          <el-card>
            <template #header>
              <div class="card-header">
                <span>经验要求分布</span>
              </div>
            </template>
            <div id="experience-chart" style="height: 300px;"></div>
          </el-card>
        </el-col>
      </el-row>
      
      <el-row :gutter="20" style="margin-top: 20px;">
        <el-col :span="12">
          <el-card>
            <template #header>
              <div class="card-header">
                <span>行业平均薪资对比</span>
              </div>
            </template>
            <div id="industry-chart" style="height: 300px;"></div>
          </el-card>
        </el-col>
        
        <el-col :span="12">
          <el-card>
            <template #header>
              <div class="card-header">
                <span>技能热度排行榜</span>
              </div>
            </template>
            <div id="skill-chart" style="height: 300px;"></div>
          </el-card>
        </el-col>
      </el-row>
    </el-card>
  </div>
</template>

<script>
import { ref, reactive, onMounted, onUnmounted, nextTick } from 'vue'
import * as echarts from 'echarts'
import { ElMessage } from 'element-plus'
import request from '@/utils/request'

export default {
  name: 'AnalysisView',
  setup() {
    const refreshing = ref(false)
    const stats = reactive({
      totalJobs: 0,
      avgSalary: 0,
      topCity: '',
      topSkill: ''
    })
    
    let cityChart = null
    let experienceChart = null
    let industryChart = null
    let skillChart = null
    
    // 刷新数据分析
    const refreshAnalysis = async () => {
      refreshing.value = true
      try {
        await loadRealTimeData()
        ElMessage.success('数据已刷新')
      } catch (error) {
        console.error('刷新数据失败:', error)
        ElMessage.error('刷新数据失败')
      } finally {
        refreshing.value = false
      }
    }
    
    // 加载实时数据
    const loadRealTimeData = async () => {
      try {
        const response = await request.get('/analysis/real-time')
        const data = response
        
        // 更新统计信息
        updateStats(data)
        
        // 更新图表
        updateCharts(data)
        
      } catch (error) {
        console.error('加载实时数据失败:', error)
        throw error
      }
    }
    
    // 更新统计信息
    const updateStats = (data) => {
      stats.totalJobs = data.total_jobs || 0
      
      // 计算平均薪资
      if (data.salaries && data.salaries.length > 0) {
        stats.avgSalary = Math.round(data.salaries.reduce((a, b) => a + b, 0) / data.salaries.length)
      }
      
      // 热门城市
      if (data.cities && data.cities.length > 0) {
        stats.topCity = data.cities[0]
      }
      
      // 热门技能
      if (data.skills && data.skills.length > 0) {
        stats.topSkill = data.skills[0]
      }
    }
    
    // 格式化函数
    const formatCity = (value) => {
      return value === 1 ? stats.topCity : '暂无'
    }
    
    const formatSkill = (value) => {
      return value === 1 ? stats.topSkill : '暂无'
    }
    
    // 更新图表
    const updateCharts = (data) => {
      // 城市薪资对比图
      if (cityChart) {
        const cityOption = {
          title: { 
            text: '城市平均薪资对比', 
            left: 'center',
            top: '10px',
            textStyle: {
              fontSize: 16,
              fontWeight: 'bold',
              color: '#333'
            }
          },
          grid: {
            top: '60px',
            bottom: '30px',
            left: '60px',
            right: '30px'
          },
          xAxis: { type: 'category', data: data.cities || [] },
          yAxis: { type: 'value', name: '薪资 (元)' },
          series: [{
            data: (data.salaries || []).map(salary => ({
              value: salary,
              itemStyle: { color: '#52c41a' }
            })),
            type: 'bar',
            label: {
              show: true,
              position: 'top',
              formatter: '{c}元',
              fontSize: 12,
              color: '#333'
            }
          }]
        }
        cityChart.setOption(cityOption)
      }
      
      // 经验要求分布图
      if (experienceChart) {
        const expOption = {
          title: { 
            text: '经验要求分布', 
            left: 'center',
            top: '10px',
            textStyle: {
              fontSize: 16,
              fontWeight: 'bold',
              color: '#333'
            }
          },
          grid: {
            top: '60px',
            bottom: '30px',
            left: '60px',
            right: '30px'
          },
          xAxis: { type: 'category', data: data.experiences || [] },
          yAxis: { type: 'value' },
          series: [{
            data: (data.counts || []).map(count => ({
              value: count,
              itemStyle: { color: '#fa8c16' }
            })),
            type: 'bar',
            label: {
              show: true,
              position: 'top',
              formatter: '{c}个',
              fontSize: 12,
              color: '#333'
            }
          }]
        }
        experienceChart.setOption(expOption)
      }
      
      // 行业薪资对比图
        if (industryChart) {
          const industryOption = {
            title: { 
              text: '行业平均薪资对比', 
              left: 'center',
              top: '10px',
              textStyle: {
                fontSize: 16,
                fontWeight: 'bold',
                color: '#333'
              }
            },
            grid: {
              top: '60px',
              bottom: '30px',
              left: '80px',
              right: '60px'
            },
            xAxis: { type: 'value', name: '薪资 (元)' },
            yAxis: { type: 'category', data: data.industries || [] },
            series: [{
              data: (data.industry_salaries || []).map(salary => ({
                value: salary,
                itemStyle: { color: '#1890ff' }
              })),
              type: 'bar',
              label: {
                show: true,
                position: 'right',
                formatter: '{c}元',
                fontSize: 12,
                color: '#333'
              }
            }]
          }
          industryChart.setOption(industryOption)
        }
      
      // 技能热度排行榜
        if (skillChart) {
          const skillOption = {
            title: { 
              text: '技能热度排行榜', 
              left: 'center',
              top: '10px',
              textStyle: {
                fontSize: 16,
                fontWeight: 'bold',
                color: '#333'
              }
            },
            grid: {
              top: '60px',
              bottom: '30px',
              left: '60px',
              right: '30px'
            },
            xAxis: { type: 'category', data: data.skills || [] },
            yAxis: { type: 'value' },
            series: [{
              data: (data.skill_counts || []).map(count => ({
                value: count,
                itemStyle: { color: '#722ed1' }
              })),
              type: 'bar',
              label: {
                show: true,
                position: 'top',
                formatter: '{c}次',
                fontSize: 12,
                color: '#333'
              }
            }]
          }
          skillChart.setOption(skillOption)
        }
    }
    
    // 初始化图表
    const initCharts = () => {
      // 确保DOM元素存在后再初始化
      const cityEl = document.getElementById('city-chart')
      const expEl = document.getElementById('experience-chart')
      const industryEl = document.getElementById('industry-chart')
      const skillEl = document.getElementById('skill-chart')
      
      // 检查是否已经初始化过
      if (!cityChart && cityEl) cityChart = echarts.init(cityEl)
      if (!experienceChart && expEl) experienceChart = echarts.init(expEl)
      if (!industryChart && industryEl) industryChart = echarts.init(industryEl)
      if (!skillChart && skillEl) skillChart = echarts.init(skillEl)
      
      // 设置默认图表（空数据）
      const emptyOption = {
        title: { text: '暂无数据', left: 'center', top: 'center' },
        xAxis: { show: false },
        yAxis: { show: false },
        series: []
      }
      
      if (cityChart) cityChart.setOption(emptyOption)
      if (experienceChart) experienceChart.setOption(emptyOption)
      if (industryChart) industryChart.setOption(emptyOption)
      if (skillChart) skillChart.setOption(emptyOption)
    }
    
    // 组件挂载时初始化
    onMounted(async () => {
      // 使用nextTick确保DOM已渲染
      await nextTick()
      initCharts()
      await loadRealTimeData()
    })
    
    // 组件卸载时销毁图表
    onUnmounted(() => {
      if (cityChart) cityChart.dispose()
      if (experienceChart) experienceChart.dispose()
      if (industryChart) industryChart.dispose()
      if (skillChart) skillChart.dispose()
    })
    
    return {
      refreshing,
      stats,
      refreshAnalysis,
      formatCity,
      formatSkill
    }
  }
}
</script>

<style scoped>
.analysis-page {
  padding: 0;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>