<template>
  <div class="admin-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <h2>数据爬取管理</h2>
          <p>手动控制数据爬取和系统管理</p>
        </div>
      </template>
      
      <!-- 数据统计 -->
      <el-row :gutter="20" style="margin-bottom: 30px;">
        <el-col :span="6">
          <el-statistic title="总职位数" :value="stats.total_jobs || 0" />
        </el-col>
        <el-col :span="6">
          <el-statistic title="上次爬取" :value="stats.last_run ? 1 : 0" :formatter="formatLastRun" />
        </el-col>
        <el-col :span="6">
          <el-statistic title="爬取状态" :value="scrapingStatus.is_running ? 1 : 0" :formatter="formatStatus" />
        </el-col>
        <el-col :span="6">
          <el-statistic title="上次爬取数量" :value="scrapingStatus.job_count || 0" />
        </el-col>
      </el-row>
      
      <!-- 爬取控制 -->
      <el-card style="margin-bottom: 20px;">
        <template #header>
          <div class="card-header">
            <span>数据爬取控制</span>
          </div>
        </template>
        
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form label-width="120px">
              <el-form-item label="数据源">
                <el-radio-group v-model="selectedSource">
                  <el-radio value="mock">模拟数据</el-radio>
                  <el-radio value="github">GitHub Jobs</el-radio>
                </el-radio-group>
              </el-form-item>
              
              <el-form-item>
                <el-button 
                  type="primary" 
                  :loading="scrapingStatus.is_running"
                  :disabled="scrapingStatus.is_running"
                  @click="triggerScraping"
                >
                  {{ scrapingStatus.is_running ? '爬取中...' : '开始爬取' }}
                </el-button>
                <el-button 
                  type="danger" 
                  :disabled="scrapingStatus.is_running || !stats.total_jobs"
                  @click="showClearDialog = true"
                >
                  清空数据
                </el-button>
              </el-form-item>
            </el-form>
          </el-col>
          
          <el-col :span="12">
            <div class="status-info">
              <h4>爬取状态信息</h4>
              <div v-if="scrapingStatus.is_running" class="running-status">
                <el-alert 
                  title="数据爬取正在进行中" 
                  type="info" 
                  :closable="false"
                  show-icon
                />
                <div class="progress-info">
                  <el-progress :percentage="50" status="success" />
                  <p>正在从 {{ selectedSource }} 获取数据...</p>
                </div>
              </div>
              <div v-else-if="scrapingStatus.error" class="error-status">
                <el-alert 
                  :title="`爬取失败: ${scrapingStatus.error}`" 
                  type="error" 
                  :closable="false"
                  show-icon
                />
              </div>
              <div v-else-if="scrapingStatus.last_run" class="success-status">
                <el-alert 
                  :title="`上次爬取成功: ${formatTime(scrapingStatus.last_run)}`" 
                  type="success" 
                  :closable="false"
                  show-icon
                />
                <p>新增职位: {{ scrapingStatus.job_count }} 条</p>
              </div>
              <div v-else class="idle-status">
                <el-alert 
                  title="爬取服务就绪" 
                  type="info" 
                  :closable="false"
                  show-icon
                />
                <p>请选择数据源并开始爬取</p>
              </div>
            </div>
          </el-col>
        </el-row>
      </el-card>
      
      <!-- 数据统计图表 -->
      <el-row :gutter="20">
        <el-col :span="12">
          <el-card>
            <template #header>
              <span>城市分布统计</span>
            </template>
            <div ref="cityChart" style="height: 300px;"></div>
          </el-card>
        </el-col>
        
        <el-col :span="12">
          <el-card>
            <template #header>
              <span>职位类别分布</span>
            </template>
            <div ref="categoryChart" style="height: 300px;"></div>
          </el-card>
        </el-col>
      </el-row>
    </el-card>
    
    <!-- 清空数据确认对话框 -->
    <el-dialog v-model="showClearDialog" title="确认清空数据" width="400px">
      <p>确定要清空所有职位数据吗？此操作不可恢复！</p>
      <template #footer>
        <el-button @click="showClearDialog = false">取消</el-button>
        <el-button type="danger" @click="clearAllData" :loading="clearing">确认清空</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script>
import { ref, reactive, onMounted, onUnmounted } from 'vue'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'
import request from '@/utils/request'

export default {
  name: 'AdminView',
  setup() {
    const selectedSource = ref('mock')
    const showClearDialog = ref(false)
    const clearing = ref(false)
    
    // 图表引用
    const cityChart = ref(null)
    const categoryChart = ref(null)
    
    // 状态数据
    const scrapingStatus = reactive({
      is_running: false,
      last_run: null,
      job_count: 0,
      error: null,
      total_jobs: 0
    })
    
    const stats = reactive({
      total_jobs: 0,
      last_run: null,
      city_stats: [],
      category_stats: []
    })
    
    // 定时器
    let statusTimer = null
    
    // 加载统计数据
    const loadStats = async () => {
      try {
        const response = await request.get('/scraping/stats')
        Object.assign(stats, response)
        
        // 更新图表
        updateCharts()
      } catch (error) {
        console.error('加载统计数据失败:', error)
      }
    }
    
    // 加载爬取状态
    const loadScrapingStatus = async () => {
      try {
        const response = await request.get('/scraping/status')
        Object.assign(scrapingStatus, response)
      } catch (error) {
        console.error('加载爬取状态失败:', error)
      }
    }
    
    // 触发爬取
    const triggerScraping = async () => {
      try {
        const response = await request.post('/scraping/trigger', {
          source: selectedSource.value
        })
        
        ElMessage.success('已开始爬取数据')
        
        // 开始轮询状态
        startStatusPolling()
      } catch (error) {
        console.error('触发爬取失败:', error)
        ElMessage.error('触发爬取失败')
      }
    }
    
    // 清空数据
    const clearAllData = async () => {
      clearing.value = true
      try {
        const response = await request.delete('/scraping/clear')
        ElMessage.success(response.message)
        showClearDialog.value = false
        
        // 重新加载统计
        await loadStats()
        await loadScrapingStatus()
      } catch (error) {
        console.error('清空数据失败:', error)
        ElMessage.error('清空数据失败')
      } finally {
        clearing.value = false
      }
    }
    
    // 开始状态轮询
    const startStatusPolling = () => {
      if (statusTimer) {
        clearInterval(statusTimer)
      }
      
      statusTimer = setInterval(async () => {
        await loadScrapingStatus()
        
        // 如果爬取完成，停止轮询并重新加载统计
        if (!scrapingStatus.is_running) {
          clearInterval(statusTimer)
          statusTimer = null
          await loadStats()
          
          if (scrapingStatus.error) {
            ElMessage.error(`爬取失败: ${scrapingStatus.error}`)
          } else {
            ElMessage.success(`爬取完成，新增 ${scrapingStatus.job_count} 条数据`)
          }
        }
      }, 2000) // 每2秒检查一次
    }
    
    // 更新图表
    const updateCharts = () => {
      if (!cityChart.value || !categoryChart.value) return
      
      // 城市分布图表
      const cityChartInstance = echarts.init(cityChart.value)
      const cityOption = {
        tooltip: {
          trigger: 'axis',
          formatter: '{b}: {c} 个职位'
        },
        xAxis: {
          type: 'category',
          data: stats.city_stats.map(item => item.city)
        },
        yAxis: {
          type: 'value'
        },
        series: [{
          data: stats.city_stats.map(item => item.count),
          type: 'bar',
          itemStyle: {
            color: '#409EFF'
          }
        }]
      }
      cityChartInstance.setOption(cityOption)
      
      // 类别分布图表
      const categoryChartInstance = echarts.init(categoryChart.value)
      const categoryOption = {
        tooltip: {
          trigger: 'item',
          formatter: '{a} <br/>{b}: {c} ({d}%)'
        },
        legend: {
          orient: 'vertical',
          left: 'left'
        },
        series: [{
          name: '职位类别',
          type: 'pie',
          radius: '50%',
          data: stats.category_stats.map(item => ({
            value: item.count,
            name: item.category
          })),
          emphasis: {
            itemStyle: {
              shadowBlur: 10,
              shadowOffsetX: 0,
              shadowColor: 'rgba(0, 0, 0, 0.5)'
            }
          }
        }]
      }
      categoryChartInstance.setOption(categoryOption)
      
      // 响应式调整
      window.addEventListener('resize', () => {
        cityChartInstance.resize()
        categoryChartInstance.resize()
      })
    }
    
    // 格式化时间
    const formatDate = (dateString) => {
      if (!dateString) return '暂无'
      const date = new Date(dateString)
      return date.toLocaleDateString('zh-CN')
    }
    
    const formatTime = (dateString) => {
      if (!dateString) return '暂无'
      const date = new Date(dateString)
      return date.toLocaleString('zh-CN')
    }
    
    // 格式化状态
    const formatStatus = (value) => {
      return value === 1 ? '运行中' : '空闲'
    }
    
    // 格式化上次爬取时间
    const formatLastRun = (value) => {
      return value === 1 ? formatDate(stats.last_run) : '暂无'
    }
    
    onMounted(async () => {
      await loadStats()
      await loadScrapingStatus()
      
      // 如果正在爬取，开始轮询
      if (scrapingStatus.is_running) {
        startStatusPolling()
      }
    })
    
    onUnmounted(() => {
      if (statusTimer) {
        clearInterval(statusTimer)
      }
    })
    
    return {
      selectedSource,
      showClearDialog,
      clearing,
      cityChart,
      categoryChart,
      scrapingStatus,
      stats,
      triggerScraping,
      clearAllData,
      formatDate,
      formatTime,
      formatStatus,
      formatLastRun
    }
  }
}
</script>

<style scoped>
.admin-page {
  padding: 0;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.status-info {
  padding: 10px;
}

.running-status,
.error-status,
.success-status,
.idle-status {
  margin-bottom: 15px;
}

.progress-info {
  margin-top: 15px;
}

.progress-info p {
  margin: 10px 0 0 0;
  text-align: center;
  color: #666;
}
</style>