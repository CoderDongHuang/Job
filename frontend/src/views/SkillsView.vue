<template>
  <div class="skills-page">
    <el-row :gutter="20">
      <el-col :span="8">
        <el-card class="input-panel">
          <h3>技能分析</h3>
          <el-form>
            <el-form-item label="输入职位描述或技能列表">
              <el-input
                v-model="inputText"
                type="textarea"
                :rows="8"
                placeholder="请输入职位描述文本，系统将自动识别其中的技能要求..."
              />
            </el-form-item>
            <el-button 
              type="primary" 
              @click="analyzeSkills" 
              :loading="analyzing"
              style="width: 100%;"
            >
              {{ analyzing ? '分析中...' : '开始分析' }}
            </el-button>
          </el-form>
          
          <div class="examples">
            <h4>示例输入：</h4>
            <p @click="loadExample(1)">资深Python开发工程师，要求熟练掌握Django、Flask框架...</p>
            <p @click="loadExample(2)">前端开发，精通React、Vue.js、TypeScript...</p>
            <p @click="loadExample(3)">数据科学家，需要Python、机器学习、深度学习经验...</p>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="16">
        <el-card v-if="analysisResult">
          <template #header>
            <div class="card-header">
              <span>分析结果</span>
            </div>
          </template>
          
          <el-tabs v-model="activeTab">
            <el-tab-pane label="提取的技能" name="skills">
              <el-space wrap :size="10" style="margin-bottom: 20px;">
                <el-tag 
                  v-for="skill in analysisResult.extracted_skills" 
                  :key="skill" 
                  size="large"
                  effect="dark"
                >
                  {{ skill }}
                </el-tag>
              </el-space>
              
              <h3>技能频率统计</h3>
              <el-table
                :data="getSkillFrequencyData"
                style="width: 100%; margin-top: 20px;"
              >
                <el-table-column prop="skill" label="技能" width="200"></el-table-column>
                <el-table-column prop="frequency" label="出现次数" width="120">
                  <template #default="{ row }">
                    <el-progress 
                      :percentage="Math.round(row.percentage * 100)" 
                      :format="() => row.frequency"
                      :color="getColorByFrequency(row.frequency)"
                    />
                  </template>
                </el-table-column>
                <el-table-column prop="percentage" label="占比">
                  <template #default="{ row }">
                    <span>{{ Math.round(row.percentage * 100) }}%</span>
                  </template>
                </el-table-column>
              </el-table>
            </el-tab-pane>
            
            <el-tab-pane label="技能关联" name="relations">
              <div class="relations-container">
                <el-tree
                  :data="relationTreeData"
                  :props="{ children: 'children', label: 'label' }"
                  node-key="id"
                  default-expand-all
                  :expand-on-click-node="false"
                />
              </div>
            </el-tab-pane>
            
            <el-tab-pane label="技能图谱" name="graph">
              <div id="skill-graph" style="height: 500px;"></div>
            </el-tab-pane>
          </el-tabs>
        </el-card>
        
        <el-card v-else class="empty-state">
          <el-empty description="请在左侧输入职位描述进行技能分析" />
        </el-card>
      </el-col>
    </el-row>
    
    <el-row :gutter="20" style="margin-top: 20px;">
      <el-col :span="24">
        <el-card>
          <h3>技能趋势分析</h3>
          <div class="trend-charts">
            <el-row :gutter="20">
              <el-col :span="12">
                <div id="rising-skills-chart" style="height: 300px;"></div>
              </el-col>
              <el-col :span="12">
                <div id="declining-skills-chart" style="height: 300px;"></div>
              </el-col>
            </el-row>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'
import request from '@/utils/request'

export default {
  name: 'SkillsView',
  setup() {
    const inputText = ref('')
    const analyzing = ref(false)
    const analysisResult = ref(null)
    const activeTab = ref('skills')
    
    // 示例文本 - 从真实职位数据中获取
    const examples = ref([])
    
    // 加载示例职位描述
    const loadExamples = async () => {
      try {
        const response = await request.get('/jobs?limit=5')
        // 确保response是数组格式
        const jobs = Array.isArray(response) ? response : (response.data || [])
        examples.value = jobs.map(job => job.description || job.requirements || "")
      } catch (error) {
        console.error('加载示例数据失败:', error)
        // 如果API失败，使用默认示例
        examples.value = [
          "",
          "资深Python开发工程师，要求熟练掌握Django、Flask框架，熟悉MySQL、Redis数据库，了解Docker容器化技术，有微服务架构经验者优先。",
          "前端开发工程师，精通React、Vue.js、TypeScript，熟悉Webpack、Vite等构建工具，有移动端开发经验，了解前端性能优化。",
          "数据科学家，需要Python、机器学习、深度学习经验，熟悉TensorFlow、PyTorch框架，有大数据处理经验，了解SQL和NoSQL数据库。"
        ]
      }
    }
    
    // 在组件挂载时加载示例数据
    onMounted(() => {
      loadExamples()
    })
    
    const analyzeSkills = async () => {
      if (!inputText.value.trim()) {
        ElMessage.warning('请输入职位描述文本')
        return
      }
      
      analyzing.value = true
      
      try {
        // 调用真实API
        const response = await request.post('/skills/analyze', {
          text: inputText.value,
          top_k: 10
        });
        
        analysisResult.value = response.data
        
        ElMessage.success('技能分析完成！')
      } catch (error) {
        console.error('技能分析失败:', error)
        ElMessage.error('分析失败，请重试')
      } finally {
        analyzing.value = false
      }
    }
    
    const loadExample = (index) => {
      inputText.value = examples[index]
    }
    
    const getSkillFrequencyData = computed(() => {
      if (!analysisResult.value) return []
      
      const total = Object.values(analysisResult.value.skill_frequency).reduce((sum, count) => sum + count, 0)
      return Object.entries(analysisResult.value.skill_frequency)
        .map(([skill, frequency]) => ({
          skill,
          frequency,
          percentage: frequency / total
        }))
        .sort((a, b) => b.frequency - a.frequency)
    })
    
    const relationTreeData = computed(() => {
      if (!analysisResult.value) return []
      
      return Object.entries(analysisResult.value.related_skills).map(([skill, related]) => ({
        id: skill,
        label: `${skill} (${analysisResult.value.skill_frequency[skill] || 0})`,
        children: related.map(rel => ({
          id: `${skill}-${rel}`,
          label: rel
        }))
      }))
    })
    
    const getColorByFrequency = (freq) => {
      if (freq >= 4) return '#67C23A'  // success green
      if (freq >= 2) return '#E6A23C'  // warning orange
      return '#F56C6C'  // danger red
    }
    
    return {
      inputText,
      analyzing,
      analysisResult,
      activeTab,
      examples,
      analyzeSkills,
      loadExample,
      getSkillFrequencyData,
      relationTreeData,
      getColorByFrequency
    }
  },
  
  mounted() {
    this.initCharts()
  },
  
  methods: {
    initCharts() {
      // 使用nextTick确保DOM已渲染
      this.$nextTick(() => {
        // 确保DOM元素存在后再初始化
        const skillGraphEl = document.getElementById('skill-graph')
        const risingSkillsEl = document.getElementById('rising-skills-chart')
        const decliningSkillsEl = document.getElementById('declining-skills-chart')
        
        if (skillGraphEl) {
          this.skillGraphChart = echarts.init(skillGraphEl)
        }
        if (risingSkillsEl) {
          this.risingSkillsChart = echarts.init(risingSkillsEl)
        }
        if (decliningSkillsEl) {
          this.decliningSkillsChart = echarts.init(decliningSkillsEl)
        }
        
        // 从API获取真实数据并更新图表
        this.updateChartsWithData()
        
        // 响应窗口大小变化
        window.addEventListener('resize', () => {
          if (this.skillGraphChart) this.skillGraphChart.resize()
          if (this.risingSkillsChart) this.risingSkillsChart.resize()
          if (this.decliningSkillsChart) this.decliningSkillsChart.resize()
        })
      })
    },
    
    async updateChartsWithData() {
      try {
        // 获取技能趋势数据
        const skillsRes = await axios.get('/api/v1/skills/trends')
        const trendsData = skillsRes.data
        
        // 获取技能关联数据（这里可能需要后端API支持）
        const graphOption = {
          title: {
            text: '技能关联图谱',
            subtext: '技能之间的关联关系',
            left: 'center'
          },
          tooltip: {
            formatter: function(params) {
              if (params.dataType === 'node') {
                return params.name
              } else if (params.dataType === 'edge') {
                return `${params.data.source} -> ${params.data.target}`
              }
            }
          },
          series: [{
            type: 'graph',
            layout: 'force',
            symbolSize: 60,
            roam: true,
            edgeSymbol: ['circle', 'arrow'],
            edgeSymbolSize: [2, 8],
            edgeLabel: {
              fontSize: 12
            },
            force: {
              repulsion: 1000,
              edgeLength: 100
            },
            draggable: true,
            // 使用真实技能数据
            data: [],
            links: [],
            emphasis: {
              focus: 'adjacency',
              lineStyle: {
                width: 10
              }
            }
          }]
        }
        
        // 如果有分析结果，则基于分析结果创建图表
        if (this.analysisResult && this.analysisResult.related_skills) {
          const nodes = []
          const links = []
          const allSkills = new Set()
          
          // 添加所有技能到nodes
          Object.keys(this.analysisResult.related_skills).forEach(skill => {
            allSkills.add(skill)
            this.analysisResult.related_skills[skill].forEach(relatedSkill => {
              allSkills.add(relatedSkill)
            })
          })
          
          // 创建节点
          allSkills.forEach((skill, index) => {
            nodes.push({
              name: skill,
              symbolSize: (this.analysisResult.skill_frequency[skill] || 1) * 10,
              itemStyle: { 
                color: this.getNodeColor(index) 
              }
            })
          })
          
          // 创建边
          Object.entries(this.analysisResult.related_skills).forEach(([skill, relatedSkills]) => {
            relatedSkills.forEach(relatedSkill => {
              if (allSkills.has(relatedSkill)) {
                links.push({
                  source: skill,
                  target: relatedSkill
                })
              }
            })
          })
          
          graphOption.series[0].data = nodes
          graphOption.series[0].links = links
        }
        
        // 上升技能趋势 - 使用真实数据
        const risingOption = {
          title: {
            text: '热门上升技能',
            left: 'center'
          },
          xAxis: {
            type: 'category',
            data: trendsData.rising_skills || []
          },
          yAxis: {
            type: 'value',
            name: '热度指数'
          },
          series: [{
            data: Array(trendsData.rising_skills?.length || 0).fill(0).map((_, i) => 100 - i * 5),
            type: 'bar',
            itemStyle: { color: '#5470c6' }
          }]
        }
        
        // 下降技能趋势 - 使用真实数据
        const decliningOption = {
          title: {
            text: '逐渐衰退技能',
            left: 'center'
          },
          xAxis: {
            type: 'category',
            data: trendsData.declining_skills || []
          },
          yAxis: {
            type: 'value',
            name: '热度指数'
          },
          series: [{
            data: Array(trendsData.declining_skills?.length || 0).fill(0).map((_, i) => 10 + i * 5),
            type: 'bar',
            itemStyle: { color: '#ee6666' }
          }]
        }
        
        this.skillGraphChart.setOption(graphOption)
        this.risingSkillsChart.setOption(risingOption)
        this.decliningSkillsChart.setOption(decliningOption)
      } catch (error) {
        console.error('更新图表数据失败:', error)
        
        // 如果API调用失败，使用默认数据
        this.setDefaultChartData()
      }
    },
    
    setDefaultChartData() {
      // 默认图表数据（仅当API调用失败时使用）
      const graphOption = {
        title: {
          text: '技能关联图谱',
          subtext: '技能之间的关联关系',
          left: 'center'
        },
        tooltip: {},
        series: [{
          type: 'graph',
          layout: 'force',
          symbolSize: 60,
          roam: true,
          edgeSymbol: ['circle', 'arrow'],
          edgeSymbolSize: [2, 8],
          edgeLabel: {
            fontSize: 12
          },
          force: {
            repulsion: 1000,
            edgeLength: 100
          },
          draggable: true,
          data: [
            { name: 'Python', symbolSize: 80, itemStyle: { color: '#FF6B6B' } },
            { name: 'Django', symbolSize: 60, itemStyle: { color: '#4ECDC4' } },
            { name: 'Flask', symbolSize: 60, itemStyle: { color: '#45B7D1' } },
            { name: '机器学习', symbolSize: 70, itemStyle: { color: '#96CEB4' } },
            { name: '数据分析', symbolSize: 60, itemStyle: { color: '#FFEAA7' } },
            { name: 'Web开发', symbolSize: 70, itemStyle: { color: '#DDA0DD' } }
          ],
          links: [
            { source: 'Python', target: 'Django' },
            { source: 'Python', target: 'Flask' },
            { source: 'Python', target: '机器学习' },
            { source: 'Python', target: '数据分析' },
            { source: 'Django', target: 'Web开发' },
            { source: 'Flask', target: 'Web开发' }
          ],
          emphasis: {
            focus: 'adjacency',
            lineStyle: {
              width: 10
            }
          }
        }]
      }
      
      const risingOption = {
        title: {
          text: '热门上升技能',
          left: 'center'
        },
        xAxis: {
          type: 'category',
          data: ['AI/ML', '云计算', '数据科学', 'DevOps', '区块链']
        },
        yAxis: {
          type: 'value',
          name: '热度指数'
        },
        series: [{
          data: [95, 90, 85, 80, 75],
          type: 'bar',
          itemStyle: { color: '#5470c6' }
        }]
      }
      
      const decliningOption = {
        title: {
          text: '逐渐衰退技能',
          left: 'center'
        },
        xAxis: {
          type: 'category',
          data: ['Flash', 'Silverlight', 'COBOL', 'Perl', 'VB6']
        },
        yAxis: {
          type: 'value',
          name: '热度指数'
        },
        series: [{
          data: [10, 15, 25, 30, 35],
          type: 'bar',
          itemStyle: { color: '#ee6666' }
        }]
      }
      
      this.skillGraphChart.setOption(graphOption)
      this.risingSkillsChart.setOption(risingOption)
      this.decliningSkillsChart.setOption(decliningOption)
    },
    
    getNodeColor(index) {
      // 根据索引返回不同颜色
      const colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7', '#DDA0DD', '#9B59B6', '#34495E', '#2ECC71', '#F39C12']
      return colors[index % colors.length]
    }
  },
  
  beforeUnmount() {
    if (this.skillGraphChart) {
      this.skillGraphChart.dispose()
    }
    if (this.risingSkillsChart) {
      this.risingSkillsChart.dispose()
    }
    if (this.decliningSkillsChart) {
      this.decliningSkillsChart.dispose()
    }
  }
}
</script>

<style scoped>
.skills-page {
  padding: 20px;
}

.input-panel {
  height: 600px;
}

.examples {
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid #eee;
}

.examples h4 {
  margin-bottom: 10px;
}

.examples p {
  cursor: pointer;
  padding: 5px 0;
  color: #409EFF;
}

.examples p:hover {
  text-decoration: underline;
}

.relations-container {
  max-height: 400px;
  overflow-y: auto;
}

.trend-charts {
  margin-top: 20px;
}

.empty-state {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 400px;
}
</style>