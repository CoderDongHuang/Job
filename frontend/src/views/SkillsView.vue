<template>
  <div class="skills-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>技能分析工具</span>
          <el-button type="primary" size="small" @click="resetAnalysis">
            <el-icon><Refresh /></el-icon>
            重置分析
          </el-button>
        </div>
      </template>
      
      <!-- 输入区域 -->
      <div class="input-section" style="margin-bottom: 30px;">
        <h3>输入职位描述</h3>
        <el-input
          v-model="inputText"
          type="textarea"
          :rows="6"
          placeholder="请输入职位描述文本，系统将自动识别其中的技能要求..."
          style="margin-bottom: 15px;"
        />
        
        <div class="input-actions">
          <el-button 
            type="primary" 
            @click="analyzeSkills" 
            :loading="analyzing"
            size="large"
          >
            <el-icon><Search /></el-icon>
            {{ analyzing ? '分析中...' : '开始分析' }}
          </el-button>
          
          <el-button-group style="margin-left: 10px;">
            <el-button @click="loadExample(1)" size="large">示例1</el-button>
            <el-button @click="loadExample(2)" size="large">示例2</el-button>
            <el-button @click="loadExample(3)" size="large">示例3</el-button>
          </el-button-group>
        </div>
      </div>
      
      <!-- 分析结果区域 -->
      <div v-if="analysisResult" class="analysis-results">
        <el-divider />
        
        <!-- 提取的技能 -->
        <div class="result-section">
          <h3>提取的技能</h3>
          <div class="skills-tags">
            <el-tag 
              v-for="skill in extractedSkills" 
              :key="skill" 
              size="large"
              type="success"
              style="margin: 5px;"
            >
              {{ skill }}
            </el-tag>
          </div>
          <div v-if="extractedSkills.length === 0" class="empty-result">
            <p>未识别到技能关键词</p>
          </div>
        </div>
        
        <!-- 水平布局的分析图表 -->
        <el-row :gutter="20" style="margin-top: 30px;">
          <!-- 技能分析趋势 -->
          <el-col :span="12">
            <el-card>
              <template #header>
                <div class="card-header">
                  <span>技能热度分析</span>
                </div>
              </template>
              <div id="skill-trend-chart" style="height: 300px;"></div>
            </el-card>
          </el-col>
          
          <!-- 技能关联分析 -->
          <el-col :span="12">
            <el-card>
              <template #header>
                <div class="card-header">
                  <span>技能关联分析</span>
                </div>
              </template>
              <div id="skill-relation-chart" style="height: 300px;"></div>
            </el-card>
          </el-col>
        </el-row>
        
        <!-- 详细分析结果 -->
        <div class="detailed-analysis" style="margin-top: 30px;">
          <h3>详细分析</h3>
          <el-descriptions :column="2" border>
            <el-descriptions-item label="技能总数">{{ extractedSkills.length }}</el-descriptions-item>
            <el-descriptions-item label="技术栈类型">{{ getTechStackType }}</el-descriptions-item>
            <el-descriptions-item label="热门技能">{{ getTopSkills }}</el-descriptions-item>
            <el-descriptions-item label="技能难度">{{ getSkillDifficulty }}</el-descriptions-item>
          </el-descriptions>
          
          <!-- 学习建议 -->
          <div class="learning-suggestions" style="margin-top: 20px; padding: 15px; background: #f8f9fa; border-radius: 8px;">
            <h4>学习建议</h4>
            <ul style="color: #666; line-height: 1.6;">
              <li v-if="extractedSkills.includes('Python')">
                <strong>Python方向：</strong>建议学习Django/Flask框架、数据分析、机器学习等技能
              </li>
              <li v-if="extractedSkills.includes('JavaScript')">
                <strong>前端方向：</strong>建议深入学习React/Vue.js、TypeScript、Node.js等
              </li>
              <li v-if="extractedSkills.some(s => ['Docker', 'Kubernetes'].includes(s))">
                <strong>运维方向：</strong>建议学习容器化、CI/CD、云原生等技术
              </li>
              <li v-else>
                <strong>通用建议：</strong>从基础编程语言开始，逐步学习相关框架和工具
              </li>
            </ul>
          </div>
        </div>
      </div>
      
      <!-- 空状态 -->
      <div v-else class="empty-state">
        <el-empty description="请输入职位描述进行技能分析" />
      </div>
    </el-card>
  </div>
</template>

<script>
import { ref, reactive, computed, onMounted, onUnmounted, nextTick } from 'vue'
import * as echarts from 'echarts'
import { ElMessage } from 'element-plus'
import request from '@/utils/request'

export default {
  name: 'SkillsView',
  setup() {
    const inputText = ref('')
    const analyzing = ref(false)
    const analysisResult = ref(null)
    
    let trendChart = null
    let relationChart = null
    
    // 示例数据
    const examples = [
      '',
      "资深Python开发工程师，要求熟练掌握Django、Flask框架，熟悉MySQL、Redis数据库，了解Docker容器化技术，有微服务架构经验者优先。具备良好的代码规范和团队协作能力。",
      "前端开发工程师，精通React、Vue.js、TypeScript，熟悉Webpack、Vite等构建工具，有移动端开发经验，了解前端性能优化。要求有良好的用户体验设计意识。",
      "数据科学家，需要Python、机器学习、深度学习经验，熟悉TensorFlow、PyTorch框架，有大数据处理经验，了解SQL和NoSQL数据库。具备数据分析和可视化能力。"
    ]
    
    // 技能关键词库
    const skillKeywords = [
      'Python', 'Java', 'JavaScript', 'TypeScript', 'Vue.js', 'React', 'Angular',
      'Node.js', 'Django', 'Flask', 'Spring', 'Spring Boot', 'MyBatis',
      'MySQL', 'PostgreSQL', 'Redis', 'MongoDB', 'Oracle', 'SQL Server',
      'Docker', 'Kubernetes', 'Jenkins', 'Git', 'Linux', 'Nginx', 'Apache',
      'TensorFlow', 'PyTorch', '机器学习', '深度学习', '人工智能', 'AI',
      '数据分析', '数据挖掘', '数据可视化', '大数据', 'Hadoop', 'Spark',
      '前端开发', '后端开发', '全栈开发', '移动端开发', '小程序开发',
      '微服务', '分布式', '高并发', '性能优化', '安全', '测试', 'DevOps'
    ]
    
    // 计算属性
    const extractedSkills = computed(() => {
      if (!analysisResult.value) return []
      return analysisResult.value.extracted_skills || []
    })
    
    const getTechStackType = computed(() => {
      const skills = extractedSkills.value
      if (skills.includes('Python') && skills.includes('Django')) return 'Python后端'
      if (skills.includes('JavaScript') && skills.includes('React')) return '前端开发'
      if (skills.includes('Java') && skills.includes('Spring')) return 'Java企业级'
      if (skills.includes('机器学习') || skills.includes('TensorFlow')) return '数据科学'
      return '混合技术栈'
    })
    
    const getTopSkills = computed(() => {
      const skills = extractedSkills.value.slice(0, 3)
      return skills.length > 0 ? skills.join('、') : '暂无'
    })
    
    const getSkillDifficulty = computed(() => {
      const skills = extractedSkills.value
      const advancedSkills = ['机器学习', '深度学习', '分布式', '高并发']
      const hasAdvanced = skills.some(skill => advancedSkills.includes(skill))
      return hasAdvanced ? '高级' : '中级'
    })
    
    // 方法
    const analyzeSkills = async () => {
      if (!inputText.value.trim()) {
        ElMessage.warning('请输入职位描述文本')
        return
      }
      
      analyzing.value = true
      
      try {
        // 模拟分析过程
        await new Promise(resolve => setTimeout(resolve, 1000))
        
        // 提取技能关键词
        const extracted = extractSkillsFromText(inputText.value)
        
        // 构建分析结果
        analysisResult.value = {
          extracted_skills: extracted,
          skill_count: extracted.length,
          analysis_time: new Date().toLocaleString()
        }
        
        // 初始化图表
        await nextTick()
        initCharts()
        
        ElMessage.success(`分析完成！共识别到 ${extracted.length} 个技能`)
      } catch (error) {
        console.error('技能分析失败:', error)
        ElMessage.error('分析失败，请重试')
      } finally {
        analyzing.value = false
      }
    }
    
    // 从文本中提取技能关键词
    const extractSkillsFromText = (text) => {
      const extracted = []
      skillKeywords.forEach(skill => {
        if (text.includes(skill)) {
          extracted.push(skill)
        }
      })
      return [...new Set(extracted)] // 去重
    }
    
    // 加载示例
    const loadExample = (index) => {
      inputText.value = examples[index]
    }
    
    // 重置分析
    const resetAnalysis = () => {
      inputText.value = ''
      analysisResult.value = null
      if (trendChart) trendChart.dispose()
      if (relationChart) relationChart.dispose()
    }
    
    // 初始化图表
    const initCharts = () => {
      // 销毁已存在的图表
      if (trendChart) trendChart.dispose()
      if (relationChart) relationChart.dispose()
      
      // 确保DOM元素存在
      setTimeout(() => {
        const trendEl = document.getElementById('skill-trend-chart')
        const relationEl = document.getElementById('skill-relation-chart')
        
        if (trendEl) {
          trendChart = echarts.init(trendEl)
          updateTrendChart()
        }
        
        if (relationEl) {
          relationChart = echarts.init(relationEl)
          updateRelationChart()
        }
      }, 100)
    }
    
    // 更新趋势图表
    const updateTrendChart = () => {
      if (!trendChart || !analysisResult.value) return
      
      const skills = extractedSkills.value
      const option = {
        title: {
          text: '技能热度趋势',
          left: 'center',
          top: '10px',
          textStyle: { fontSize: 16, fontWeight: 'bold', color: '#333' }
        },
        grid: { top: '60px', bottom: '30px', left: '60px', right: '30px' },
        xAxis: {
          type: 'category',
          data: skills,
          axisLabel: { color: '#333' }
        },
        yAxis: {
          type: 'value',
          name: '热度',
          axisLabel: { color: '#333' }
        },
        series: [{
          data: skills.map((_, index) => ({
            value: parseFloat((Math.random() * 100 + 50).toFixed(2)),
            itemStyle: { color: '#1890ff' }
          })),
          type: 'bar',
          label: {
            show: true,
            position: 'top',
            formatter: (params) => {
              return parseFloat(params.value).toFixed(2)
            },
            fontSize: 12,
            color: '#333'
          }
        }]
      }
      
      trendChart.setOption(option)
    }
    
    // 更新关联图表
    const updateRelationChart = () => {
      if (!relationChart || !analysisResult.value) return
      
      const skills = extractedSkills.value.slice(0, 8)
      const option = {
        title: {
          text: '技能关联度',
          left: 'center',
          top: '10px',
          textStyle: { 
            fontSize: 16, 
            fontWeight: 'bold',
            color: '#333'
          }
        },
        grid: { 
          top: '80px', 
          bottom: '30px', 
          left: '60px', 
          right: '30px' 
        },
        radar: {
          center: ['50%', '55%'],
          radius: '65%',
          indicator: skills.map(skill => ({ 
            name: skill, 
            max: 100 
          })),
          axisName: { 
            color: '#333',
            fontSize: 12
          },
          axisLine: {
            lineStyle: {
              color: '#ccc'
            }
          },
          splitLine: {
            lineStyle: {
              color: '#eee'
            }
          }
        },
        series: [{
          type: 'radar',
          data: [{
            value: skills.map(() => parseFloat((Math.random() * 80 + 20).toFixed(2))),
            name: '技能关联度',
            areaStyle: { 
              color: 'rgba(255, 153, 0, 0.3)' 
            },
            lineStyle: { 
              color: '#ff9900',
              width: 2
            },
            itemStyle: {
              color: '#ff9900'
            },
            label: {
              show: true,
              formatter: (params) => {
                return parseFloat(params.value).toFixed(2)
              },
              color: '#333'
            }
          }]
        }]
      }
      
      relationChart.setOption(option)
    }
    
    // 组件挂载时初始化
    onMounted(() => {
      // 可以加载一些默认数据
    })
    
    // 组件卸载时销毁图表
    onUnmounted(() => {
      if (trendChart) trendChart.dispose()
      if (relationChart) relationChart.dispose()
    })
    
    return {
      inputText,
      analyzing,
      analysisResult,
      extractedSkills,
      getTechStackType,
      getTopSkills,
      getSkillDifficulty,
      analyzeSkills,
      loadExample,
      resetAnalysis
    }
  }
}
</script>

<style scoped>
.skills-page {
  padding: 0;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.input-section {
  padding: 0 20px;
}

.input-actions {
  display: flex;
  align-items: center;
}

.skills-tags {
  display: flex;
  flex-wrap: wrap;
  margin-top: 10px;
}

.result-section {
  margin-bottom: 30px;
}

.empty-result {
  text-align: center;
  color: #999;
  padding: 20px 0;
}

.empty-state {
  text-align: center;
  padding: 40px 0;
}
</style>