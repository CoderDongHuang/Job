<template>
  <div class="dashboard-page">
    <!-- 未登录提示 -->
    <div v-if="!isLoggedIn" class="login-prompt">
      <el-card>
        <el-empty description="请先登录以查看个人中心">
          <el-button type="primary" @click="goToLogin">立即登录</el-button>
        </el-empty>
      </el-card>
    </div>
    
    <!-- 已登录内容 -->
    <div v-else>
      <el-row :gutter="20">
        <!-- 左侧：用户信息 -->
        <el-col :span="8">
          <el-card class="user-profile">
            <div class="profile-header">
              <el-avatar :size="80" :src="userAvatar" />
              <div class="profile-info">
                <h3>{{ userInfo.full_name || userInfo.username }}</h3>
                <p>{{ userInfo.title || '未设置职位' }}</p>
                <p class="user-location">
                  <el-icon><Location /></el-icon>
                  {{ userInfo.location || '未设置城市' }}
                </p>
              </div>
            </div>
            
            <div class="profile-stats">
              <div class="stat-item">
                <div class="stat-value">{{ userInfo.experience_years || 0 }}</div>
                <div class="stat-label">工作经验(年)</div>
              </div>
              <div class="stat-item">
                <div class="stat-value">{{ userInfo.current_salary ? (userInfo.current_salary/1000).toFixed(0) + 'K' : '--' }}</div>
                <div class="stat-label">当前薪资</div>
              </div>
              <div class="stat-item">
                <div class="stat-value">{{ userInfo.target_salary ? (userInfo.target_salary/1000).toFixed(0) + 'K' : '--' }}</div>
                <div class="stat-label">期望薪资</div>
              </div>
            </div>
            
            <el-divider />
            
            <!-- 编辑个人信息按钮 -->
            <div class="profile-actions">
              <el-button type="primary" @click="showEditDialog = true" style="margin-right: 10px;">
                编辑个人信息
              </el-button>
              <el-button type="default" @click="goToDataManagement">
                数据管理
              </el-button>
            </div>
          </el-card>
          
          <!-- 用户技能 -->
          <el-card class="user-skills" style="margin-top: 20px;">
            <template #header>
              <div class="card-header">
                <span>我的技能</span>
                <div class="header-actions">
                  <el-button type="primary" size="small" @click="showSkillEdit = true">编辑技能</el-button>
                </div>
              </div>
            </template>
            
            <div v-if="userInfo.skills && userInfo.skills.length > 0" class="skills-list">
              <el-tag 
                v-for="skill in userInfo.skills" 
                :key="skill" 
                size="medium"
                closable
                @close="removeSkill(skill)"
                style="margin: 4px;"
              >
                {{ skill }}
              </el-tag>
            </div>
            <div v-else class="empty-skills">
              <p>暂无技能，点击编辑添加</p>
            </div>
          </el-card>
        </el-col>
        
        <!-- 右侧：推荐内容 -->
        <el-col :span="16">
          <el-card class="recommendations">
            <template #header>
              <div class="card-header">
                <span>个性化推荐</span>
                <div class="header-actions">
                  <el-button type="primary" size="small" @click="loadRecommendations">刷新推荐</el-button>
                  <el-button type="default" size="small" @click="goToJobSearch">查看更多职位</el-button>
                </div>
              </div>
            </template>
            
            <el-tabs v-model="activeTab">
              <!-- 职位推荐 -->
              <el-tab-pane label="职位推荐" name="jobs">
                <div class="recommendation-list">
                  <el-card 
                    v-for="job in recommendedJobs" 
                    :key="job.id" 
                    class="recommendation-item"
                    style="margin-bottom: 15px;"
                  >
                    <div class="job-recommendation">
                      <div class="job-info">
                        <h4>{{ job.title }}</h4>
                        <p class="job-company">{{ job.company }}</p>
                        <p class="job-details">
                          <el-tag size="small" type="warning">{{ job.city }}</el-tag>
                          <el-tag size="small" type="success">{{ (job.salary_min/1000).toFixed(0) }}K-{{ (job.salary_max/1000).toFixed(0) }}K</el-tag>
                          <el-tag size="small">{{ job.experience_required }}</el-tag>
                        </p>
                      </div>
                      <div class="job-match">
                        <el-progress 
                          :percentage="job.matchScore || 75" 
                          :stroke-width="20" 
                          :color="getMatchColor(job.matchScore || 75)"
                          :format="() => `${job.matchScore || 75}%`"
                        />
                        <p>匹配度</p>
                      </div>
                    </div>
                  </el-card>
                </div>
              </el-tab-pane>
              
              <!-- 技能提升 -->
              <el-tab-pane label="技能提升" name="skills">
                <div class="skills-recommendation">
                  <!-- 当前技能分析 -->
                  <div class="current-skills-analysis" style="margin-bottom: 30px;">
                    <h4>当前技能分析</h4>
                    <div v-if="userInfo.skills && userInfo.skills.length > 0" class="skills-tags">
                      <el-tag 
                        v-for="skill in userInfo.skills" 
                        :key="skill" 
                        size="large" 
                        type="success"
                        style="margin: 5px;"
                      >
                        {{ skill }}
                      </el-tag>
                    </div>
                    <div v-else class="empty-skills">
                      <p>暂无技能，请先添加您的技能</p>
                    </div>
                  </div>
                  
                  <!-- 个性化技能推荐 -->
                  <h4>个性化技能推荐</h4>
                  <p class="recommendation-desc">基于您当前的技能组合，为您推荐以下高价值技能：</p>
                  
                  <el-table :data="recommendedSkills" style="width: 100%;">
                    <el-table-column prop="skill" label="推荐技能" width="150">
                      <template #default="{ row }">
                        <el-tag type="warning">{{ row.skill }}</el-tag>
                      </template>
                    </el-table-column>
                    <el-table-column prop="reason" label="推荐理由" min-width="200">
                      <template #default="{ row }">
                        <span style="font-size: 12px; color: #666;">{{ row.reason }}</span>
                      </template>
                    </el-table-column>
                    <el-table-column prop="importance" label="重要性" width="100">
                      <template #default="{ row }">
                        <el-rate 
                          v-model="row.importance" 
                          disabled 
                          show-score 
                          score-template="{value}"
                          :max="5"
                        />
                      </template>
                    </el-table-column>
                    <el-table-column prop="benefit" label="薪资提升" width="100">
                      <template #default="{ row }">
                        <span style="color: #67c23a; font-weight: bold;">+{{ row.benefit }}%</span>
                      </template>
                    </el-table-column>
                    <el-table-column prop="learningTime" label="学习周期" width="100">
                      <template #default="{ row }">
                        {{ row.learningTime }}个月
                      </template>
                    </el-table-column>
                  </el-table>
                  
                  <!-- 个性化学习路径 -->
                  <h4 style="margin-top: 30px;">个性化学习路径</h4>
                  <el-steps :space="150" :active="0" align-center style="margin-top: 20px;">
                    <el-step 
                      v-for="step in generateLearningPath(userInfo.skills || [])" 
                      :key="step.step"
                      :title="step.title" 
                      :description="`${step.skills.join('、')} | ${step.duration}`"
                      style="min-width: 120px;"
                    />
                  </el-steps>
                  
                  <!-- 技能发展建议 -->
                  <div class="development-suggestions" style="margin-top: 30px; padding: 20px; background: #f8f9fa; border-radius: 8px;">
                    <h4>技能发展建议</h4>
                    <ul style="color: #666; line-height: 1.6;">
                      <li v-if="userInfo.skills && userInfo.skills.includes('Python')">
                        <strong>Python开发者：</strong>建议向数据科学或后端开发方向发展，学习Django/Flask框架和数据分析技能
                      </li>
                      <li v-if="userInfo.skills && userInfo.skills.includes('JavaScript')">
                        <strong>JavaScript开发者：</strong>建议学习TypeScript提升代码质量，掌握现代前端框架和Node.js
                      </li>
                      <li v-if="userInfo.skills && userInfo.skills.some(s => ['Vue.js', 'React'].includes(s))">
                        <strong>前端开发者：</strong>建议向全栈发展，学习后端技术和数据库知识
                      </li>
                      <li v-else>
                        <strong>新手建议：</strong>从基础编程语言开始，逐步学习Web开发和数据库知识
                      </li>
                    </ul>
                  </div>
                </div>
              </el-tab-pane>
              
              <!-- 薪资评估 -->
              <el-tab-pane label="薪资评估" name="salary">
                <div class="salary-assessment">
                  <h4>当前市场价值评估</h4>
                  <div class="salary-range">
                    <p>基于您的技能和经验，合理薪资范围：</p>
                    <p class="salary-value">¥{{ salaryAnalysis?.reasonable_min ? (salaryAnalysis.reasonable_min/1000).toFixed(0) : '--' }}K - ¥{{ salaryAnalysis?.reasonable_max ? (salaryAnalysis.reasonable_max/1000).toFixed(0) : '--' }}K</p>
                    
                    <div v-if="salaryAnalysis?.current_salary > 0" class="salary-comparison">
                      <p>当前薪资：<span class="current-salary">¥{{ (salaryAnalysis?.current_salary/1000).toFixed(0) || '--' }}K</span></p>
                      <p>期望薪资：<span class="target-salary">¥{{ (salaryAnalysis?.target_salary/1000).toFixed(0) || '--' }}K</span></p>
                      <p>薪资差距：<span :class="salaryComparison.class">{{ salaryComparison.text }}</span></p>
                    </div>
                    <div v-else class="salary-comparison">
                      <p>请先设置您的当前薪资以获取更精准的评估</p>
                    </div>
                  </div>
                  
                  <h4 style="margin-top: 20px;">影响薪资的关键因素</h4>
                  <el-table :data="salaryFactors" style="width: 100%;">
                    <el-table-column prop="factor" label="因素" width="150" />
                    <el-table-column prop="impact" label="影响程度" width="120">
                      <template #default="{ row }">
                        <el-progress 
                          :percentage="row.impact" 
                          :color="getImpactColor(row.impact)"
                        />
                      </template>
                    </el-table-column>
                    <el-table-column prop="value" label="当前水平" />
                  </el-table>
                  
                  <div v-if="salaryAnalysis?.salary_gap > 0" class="salary-suggestions" style="margin-top: 20px; padding: 15px; background: #f0f9ff; border-radius: 8px;">
                    <h4>薪资提升建议</h4>
                    <ul style="color: #666; line-height: 1.6;">
                      <li>提升技能匹配度：学习当前热门技术，如TypeScript、Docker等</li>
                      <li>增加工作经验：每增加一年经验，薪资可提升约10-15%</li>
                      <li>考虑城市发展：一线城市薪资普遍比二三线城市高20-30%</li>
                      <li>关注行业趋势：AI、大数据、云计算等方向薪资增长较快</li>
                    </ul>
                  </div>
                </div>
              </el-tab-pane>
            </el-tabs>
          </el-card>
        </el-col>
      </el-row>
    </div>
    
    <!-- 编辑个人信息对话框 -->
    <el-dialog v-model="showEditDialog" title="编辑个人信息" width="600px">
      <el-form :model="editForm" label-width="100px">
        <el-form-item label="姓名">
          <el-input v-model="editForm.full_name" placeholder="请输入姓名" />
        </el-form-item>
        <el-form-item label="职位">
          <el-input v-model="editForm.title" placeholder="请输入职位" />
        </el-form-item>
        <el-form-item label="工作经验">
          <el-input-number v-model="editForm.experience_years" :min="0" :max="50" />
          <span style="margin-left: 10px;">年</span>
        </el-form-item>
        <el-form-item label="当前薪资">
          <el-input-number v-model="editForm.current_salary" :min="0" :step="1000" />
          <span style="margin-left: 10px;">元/月</span>
        </el-form-item>
        <el-form-item label="期望薪资">
          <el-input-number v-model="editForm.target_salary" :min="0" :step="1000" />
          <span style="margin-left: 10px;">元/月</span>
        </el-form-item>
        <el-form-item label="所在城市">
          <el-select v-model="editForm.location" placeholder="请选择城市">
            <el-option label="北京" value="北京" />
            <el-option label="上海" value="上海" />
            <el-option label="深圳" value="深圳" />
            <el-option label="广州" value="广州" />
            <el-option label="杭州" value="杭州" />
            <el-option label="成都" value="成都" />
          </el-select>
        </el-form-item>
        <el-form-item label="学历">
          <el-select v-model="editForm.education" placeholder="请选择学历">
            <el-option label="大专" value="大专" />
            <el-option label="本科" value="本科" />
            <el-option label="硕士" value="硕士" />
            <el-option label="博士" value="博士" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showEditDialog = false">取消</el-button>
        <el-button type="primary" @click="saveProfile" :loading="saving">保存</el-button>
      </template>
    </el-dialog>
    
    <!-- 编辑技能对话框 -->
    <el-dialog v-model="showSkillEdit" title="编辑技能" width="600px">
      <el-form label-width="80px">
        <el-form-item label="我的技能">
          <!-- 可输入和选择的技能输入框 -->
          <el-select
            v-model="selectedSkills"
            multiple
            filterable
            allow-create
            default-first-option
            placeholder="请选择或输入技能"
            style="width: 100%;"
          >
            <el-option
              v-for="skill in allSkills"
              :key="skill"
              :label="skill"
              :value="skill"
            />
          </el-select>
          
          <div style="margin-top: 10px; font-size: 12px; color: #666;">
            <p><strong>使用说明：</strong></p>
            <ul style="margin: 5px 0; padding-left: 15px;">
              <li>可以从下拉列表选择常用技能</li>
              <li>也可以直接输入自定义技能</li>
              <li>支持多选，用逗号分隔</li>
              <li>点击标签右上角的×可以删除技能</li>
            </ul>
          </div>
          
          <!-- 当前已选技能预览 -->
          <div v-if="selectedSkills.length > 0" style="margin-top: 15px;">
            <p style="font-size: 12px; color: #666; margin-bottom: 5px;">已选技能：</p>
            <div class="selected-skills-preview">
              <el-tag 
                v-for="skill in selectedSkills" 
                :key="skill" 
                size="small" 
                closable
                @close="removeSelectedSkill(skill)"
                style="margin: 3px;"
              >
                {{ skill }}
              </el-tag>
            </div>
          </div>
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="showSkillEdit = false">取消</el-button>
        <el-button type="primary" @click="saveSkills" :loading="savingSkills">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Location } from '@element-plus/icons-vue'
import request from '@/utils/request'

export default {
  name: 'DashboardView',
  components: {
    Location
  },
  setup() {
    const router = useRouter()
    const activeTab = ref('jobs')
    
    // 用户认证状态
    const isLoggedIn = computed(() => {
      return !!localStorage.getItem('token')
    })
    
    const userInfo = ref({})
    const userAvatar = computed(() => {
      return `https://api.dicebear.com/7.x/avataaars/svg?seed=${userInfo.value?.username || 'user'}`
    })
    
    // 推荐数据
    const recommendedJobs = ref([])
    const recommendedSkills = ref([])
    
    // 编辑对话框
    const showEditDialog = ref(false)
    const showSkillEdit = ref(false)
    const saving = ref(false)
    const savingSkills = ref(false)
    
    const editForm = reactive({
      full_name: '',
      title: '',
      experience_years: 0,
      current_salary: 0,
      target_salary: 0,
      location: '',
      education: ''
    })
    
    const skillInput = ref('')
    const selectedSkills = ref([])
    
    // 所有可用技能（常用技能 + 扩展技能）
    const allSkills = ref([
      'Python', 'Java', 'JavaScript', 'TypeScript', 'Vue.js', 'React',
      'MySQL', 'Redis', 'Docker', 'Kubernetes', 'Git', 'Linux',
      '机器学习', '数据分析', '前端开发', '后端开发', 'DevOps',
      'HTML5', 'CSS3', 'Node.js', 'Spring', 'Django', 'Flask',
      'MongoDB', 'PostgreSQL', 'Redis', 'Nginx', 'Apache',
      'TensorFlow', 'PyTorch', 'Scikit-learn', 'Pandas', 'NumPy',
      'Webpack', 'Vite', 'Babel', 'ESLint', 'Jest', 'Cypress',
      'AWS', 'Azure', 'GCP', '阿里云', '腾讯云', '华为云',
      '微服务', '分布式', '高并发', '性能优化', '安全', '测试'
    ])
    
    // 薪资评估数据
    const salaryRange = ref({ min: 15000, max: 25000 })
    const salaryComparison = ref({ class: 'text-success', text: '+25%' })
    const salaryFactors = ref([
      { factor: '技能匹配度', impact: 85, value: '良好' },
      { factor: '工作经验', impact: 70, value: '3年' },
      { factor: '学历背景', impact: 60, value: '本科' },
      { factor: '所在城市', impact: 80, value: '一线城市' }
    ])
    const salaryAnalysis = ref({
      reasonable_min: 0,
      reasonable_max: 0,
      current_salary: 0,
      target_salary: 0,
      salary_gap: 0
    })
    
    // 加载用户信息
    const loadUserInfo = async () => {
      if (!isLoggedIn.value) return
      
      try {
        const response = await request.get('/users/me')
        userInfo.value = response
        
        // 初始化编辑表单
        Object.assign(editForm, {
          full_name: response.full_name || '',
          title: response.title || '',
          experience_years: response.experience_years || 0,
          current_salary: response.current_salary || 0,
          target_salary: response.target_salary || 0,
          location: response.location || '',
          education: response.education || ''
        })
        
        // 初始化技能输入
        if (response.skills && response.skills.length > 0) {
          skillInput.value = response.skills.join(', ')
        }
        
        // 加载推荐数据
        await loadRecommendations()
      } catch (error) {
        console.error('加载用户信息失败:', error)
        ElMessage.error('加载用户信息失败')
      }
    }
    
    // 加载推荐数据
    const loadRecommendations = async () => {
      if (!isLoggedIn.value) return
      
      try {
        const response = await request.get('/users/me/recommendations')
        
        // 更新职位推荐
        if (response.recommended_jobs) {
          recommendedJobs.value = response.recommended_jobs
        }
        
        // 更新薪资评估数据
        if (response.salary_analysis) {
          salaryAnalysis.value = response.salary_analysis
          
          // 更新薪资范围
          salaryRange.value = {
            min: response.salary_analysis.reasonable_min,
            max: response.salary_analysis.reasonable_max
          }
          
          // 更新薪资比较
          if (response.salary_analysis.current_salary > 0) {
            const gap = response.salary_analysis.salary_gap
            const percentage = Math.round((gap / response.salary_analysis.current_salary) * 100)
            salaryComparison.value = {
              class: gap >= 0 ? 'text-success' : 'text-danger',
              text: gap >= 0 ? `+${percentage}%` : `${percentage}%`
            }
          }
          
          // 更新薪资影响因素
          updateSalaryFactors(response.salary_analysis)
        }
        
        // 更新技能推荐
        if (response.skill_gap_analysis) {
          updateSkillRecommendations(response.skill_gap_analysis)
        }
        
      } catch (error) {
        console.error('加载推荐数据失败:', error)
        // 如果后端API不可用，使用前端算法
        recommendedJobs.value = generateFallbackJobs()
        recommendedSkills.value = analyzeSkillsAndRecommend()
      }
    }
    
    // 更新薪资影响因素
    const updateSalaryFactors = (analysis) => {
      const userSkills = userInfo.value.skills || []
      const experience = userInfo.value.experience_years || 0
      const location = userInfo.value.location || '未知'
      const education = userInfo.value.education || '未知'
      
      salaryFactors.value = [
        { 
          factor: '技能匹配度', 
          impact: Math.min(100, Math.max(30, userSkills.length * 10)), 
          value: userSkills.length > 0 ? `${userSkills.length}个技能` : '无技能'
        },
        { 
          factor: '工作经验', 
          impact: Math.min(100, experience * 15), 
          value: experience > 0 ? `${experience}年` : '应届生'
        },
        { 
          factor: '学历背景', 
          impact: getEducationImpact(education), 
          value: education || '未知'
        },
        { 
          factor: '所在城市', 
          impact: getLocationImpact(location), 
          value: location || '未知'
        }
      ]
    }
    
    // 获取学历影响因子
    const getEducationImpact = (education) => {
      const impacts = {
        '博士': 90,
        '硕士': 80,
        '本科': 70,
        '大专': 60,
        '未知': 50
      }
      return impacts[education] || 50
    }
    
    // 获取城市影响因子
    const getLocationImpact = (location) => {
      const impacts = {
        '北京': 90, '上海': 90, '深圳': 85, '广州': 80,
        '杭州': 85, '成都': 75, '南京': 75, '武汉': 70
      }
      return impacts[location] || 65
    }
    
    // 更新技能推荐
    const updateSkillRecommendations = (gapAnalysis) => {
      if (gapAnalysis.missing_skills && gapAnalysis.missing_skills.length > 0) {
        recommendedSkills.value = gapAnalysis.missing_skills.map(skill => ({
          skill,
          importance: 5,
          benefit: 20,
          learningTime: 3,
          reason: `掌握${skill}可以提升${gapAnalysis.target_role}岗位竞争力`
        }))
      } else {
        recommendedSkills.value = analyzeSkillsAndRecommend()
      }
    }
    
    // 生成备选职位推荐
    const generateFallbackJobs = () => {
      const userSkills = userInfo.value.skills || []
      const location = userInfo.value.location || '北京'
      
      return [
        {
          id: 1,
          title: '高级开发工程师',
          company: '知名互联网公司',
          city: location,
          salary_min: 15000,
          salary_max: 30000,
          experience_required: '3-5年',
          match_score: 75,
          matched_skills: userSkills.slice(0, 3),
          missing_skills: ['TypeScript', 'Docker']
        },
        {
          id: 2,
          title: '全栈开发工程师',
          company: '科技创业公司',
          city: location,
          salary_min: 12000,
          salary_max: 25000,
          experience_required: '2-4年',
          match_score: 65,
          matched_skills: userSkills.slice(0, 2),
          missing_skills: ['React', 'Node.js']
        }
      ]
    }
    
    // 技能关联图谱 - 定义技能之间的关联关系
    const skillGraph = {
      'Python': ['Django', 'Flask', '爬虫', '数据分析', '机器学习', '自动化测试'],
      'Java': ['Spring', '微服务', '分布式', 'Spring Boot', 'MyBatis'],
      'JavaScript': ['Vue.js', 'React', 'Node.js', 'TypeScript', 'Webpack'],
      'Vue.js': ['Vuex', 'Vue Router', 'Element Plus', 'Vite', 'TypeScript'],
      'React': ['Redux', 'React Router', 'Next.js', 'TypeScript', 'Webpack'],
      'MySQL': ['SQL优化', '索引优化', 'Redis', 'MongoDB', '数据库设计'],
      'Redis': ['缓存策略', '分布式锁', '消息队列', '性能优化'],
      'Docker': ['Kubernetes', 'CI/CD', '容器编排', '云原生'],
      '机器学习': ['深度学习', 'TensorFlow', 'PyTorch', '数据分析', '自然语言处理'],
      '数据分析': ['Python', 'SQL', '数据可视化', '统计学', '业务分析'],
      '前端开发': ['JavaScript', 'CSS3', 'HTML5', '响应式设计', '性能优化'],
      '后端开发': ['Java', 'Python', 'MySQL', 'Redis', 'API设计'],
      'DevOps': ['Docker', 'Kubernetes', 'CI/CD', '监控', '自动化部署']
    }

    // 技能学习难度和市场需求
    const skillMetadata = {
      'Python': { difficulty: 2, demand: 5, salaryBoost: 25 },
      'Java': { difficulty: 3, demand: 4, salaryBoost: 20 },
      'JavaScript': { difficulty: 2, demand: 5, salaryBoost: 22 },
      'Vue.js': { difficulty: 2, demand: 4, salaryBoost: 18 },
      'React': { difficulty: 3, demand: 5, salaryBoost: 25 },
      'MySQL': { difficulty: 2, demand: 4, salaryBoost: 15 },
      'Redis': { difficulty: 2, demand: 3, salaryBoost: 12 },
      'Docker': { difficulty: 3, demand: 4, salaryBoost: 20 },
      'Kubernetes': { difficulty: 4, demand: 3, salaryBoost: 25 },
      '机器学习': { difficulty: 5, demand: 4, salaryBoost: 35 },
      '数据分析': { difficulty: 3, demand: 4, salaryBoost: 22 },
      'TypeScript': { difficulty: 2, demand: 4, salaryBoost: 18 },
      'Django': { difficulty: 3, demand: 3, salaryBoost: 16 },
      'Spring': { difficulty: 4, demand: 4, salaryBoost: 22 },
      'Node.js': { difficulty: 3, demand: 4, salaryBoost: 20 }
    }

    // 智能分析用户技能并推荐相关技能
    const analyzeSkillsAndRecommend = () => {
      const userSkills = userInfo.value.skills || []
      
      if (userSkills.length === 0) {
        // 如果用户没有技能，推荐基础技能
        return [
          { skill: 'Python', importance: 5, benefit: 25, learningTime: 3, reason: '入门简单，应用广泛' },
          { skill: 'JavaScript', importance: 5, benefit: 22, learningTime: 2, reason: '前端开发必备' },
          { skill: 'MySQL', importance: 4, benefit: 15, learningTime: 2, reason: '数据库基础' },
          { skill: 'Git', importance: 3, benefit: 10, learningTime: 1, reason: '版本控制工具' }
        ]
      }

      // 分析用户技能组合
      const recommendations = new Set()
      
      // 基于当前技能推荐关联技能
      userSkills.forEach(skill => {
        if (skillGraph[skill]) {
          skillGraph[skill].forEach(relatedSkill => {
            if (!userSkills.includes(relatedSkill)) {
              recommendations.add(relatedSkill)
            }
          })
        }
      })

      // 转换为推荐列表并排序
      const recommendedList = Array.from(recommendations).map(skill => {
        const meta = skillMetadata[skill] || { difficulty: 3, demand: 3, salaryBoost: 15 }
        return {
          skill,
          importance: meta.demand,
          benefit: meta.salaryBoost,
          learningTime: meta.difficulty,
          reason: getRecommendationReason(skill, userSkills)
        }
      })

      // 按重要性和薪资提升排序
      return recommendedList.sort((a, b) => {
        const scoreA = a.importance * 2 + a.benefit
        const scoreB = b.importance * 2 + b.benefit
        return scoreB - scoreA
      }).slice(0, 6) // 取前6个推荐
    }

    // 生成推荐理由
    const getRecommendationReason = (skill, userSkills) => {
      const reasons = {
        'TypeScript': '基于JavaScript的强类型语言，提升代码质量',
        'Docker': '容器化技术，现代化部署必备',
        'Kubernetes': '容器编排工具，云原生核心技术',
        '机器学习': 'AI时代核心技术，高薪岗位需求大',
        '数据分析': '数据驱动决策，业务价值高',
        'Vue.js': '渐进式框架，学习曲线平缓',
        'React': '大型项目首选，生态丰富',
        'Spring': 'Java企业级开发框架',
        'Node.js': 'JavaScript全栈开发'
      }
      
      // 如果用户有相关基础技能，生成更具体的理由
      if (userSkills.includes('JavaScript') && skill === 'TypeScript') {
        return '您已掌握JavaScript，学习TypeScript可以提升代码质量'
      }
      if (userSkills.includes('Python') && skill === '机器学习') {
        return 'Python是机器学习的主要语言，适合深入学习'
      }
      
      return reasons[skill] || '市场需求大，职业发展前景好'
    }

    // 生成学习路径
    const generateLearningPath = (userSkills) => {
      if (userSkills.length === 0) {
        return [
          { step: 1, title: '编程基础', skills: ['Python基础', 'Git使用'], duration: '1个月' },
          { step: 2, title: 'Web开发', skills: ['HTML/CSS', 'JavaScript'], duration: '2个月' },
          { step: 3, title: '数据库', skills: ['MySQL基础'], duration: '1个月' },
          { step: 4, title: '框架学习', skills: ['Vue.js或React'], duration: '2个月' }
        ]
      }

      // 根据用户现有技能生成个性化路径
      const path = []
      
      if (userSkills.some(s => ['Python', 'Java', 'JavaScript'].includes(s))) {
        path.push({ step: 1, title: '技能深化', skills: ['框架学习', '性能优化'], duration: '2个月' })
      }
      
      if (userSkills.includes('前端开发') || userSkills.some(s => ['Vue.js', 'React'].includes(s))) {
        path.push({ step: path.length + 1, title: '全栈发展', skills: ['Node.js', '数据库设计'], duration: '3个月' })
      }
      
      if (userSkills.some(s => ['Docker', 'Linux'].includes(s))) {
        path.push({ step: path.length + 1, title: '运维能力', skills: ['Kubernetes', 'CI/CD'], duration: '2个月' })
      }
      
      if (userSkills.includes('Python') && !userSkills.includes('机器学习')) {
        path.push({ step: path.length + 1, title: 'AI方向', skills: ['机器学习基础', '数据分析'], duration: '4个月' })
      }

      return path.length > 0 ? path : [
        { step: 1, title: '职业规划', skills: ['技能评估', '方向选择'], duration: '1个月' }
      ]
    }


    
    // 保存个人信息
    const saveProfile = async () => {
      saving.value = true
      try {
        await request.put('/users/me', editForm)
        ElMessage.success('个人信息更新成功')
        showEditDialog.value = false
        await loadUserInfo() // 重新加载用户信息
      } catch (error) {
        console.error('保存个人信息失败:', error)
        ElMessage.error('保存失败')
      } finally {
        saving.value = false
      }
    }
    
    // 打开技能编辑对话框时初始化数据
    const initSkillEdit = () => {
      selectedSkills.value = userInfo.value.skills ? [...userInfo.value.skills] : []
    }

    // 保存技能
    const saveSkills = async () => {
      savingSkills.value = true
      try {
        // 使用选中的技能列表
        const skills = [...selectedSkills.value]
        
        // 调用API保存技能
        await request.put('/users/me/skills', { skills })
        
        // 更新本地数据
        userInfo.value.skills = skills
        
        ElMessage.success('技能保存成功')
        showSkillEdit.value = false
      } catch (error) {
        console.error('保存技能失败:', error)
        ElMessage.error('保存技能失败')
      } finally {
        savingSkills.value = false
      }
    }
    
    // 删除已选技能
    const removeSelectedSkill = (skill) => {
      const index = selectedSkills.value.indexOf(skill)
      if (index > -1) {
        selectedSkills.value.splice(index, 1)
      }
    }
    
    // 删除技能标签
    const removeSkill = async (skill) => {
      try {
        const skills = userInfo.value.skills.filter(s => s !== skill)
        
        // 调用API更新技能
        await request.put('/users/me/skills', { skills })
        
        // 更新本地数据
        userInfo.value.skills = skills
        
        ElMessage.success('技能删除成功')
      } catch (error) {
        console.error('删除技能失败:', error)
        ElMessage.error('删除技能失败')
      }
    }
    
    // 工具函数
    const getMatchColor = (percentage) => {
      if (percentage >= 80) return '#67c23a'
      if (percentage >= 60) return '#e6a23c'
      return '#f56c6c'
    }
    
    const getImpactColor = (percentage) => {
      if (percentage >= 80) return '#67c23a'
      if (percentage >= 60) return '#e6a23c'
      return '#f56c6c'
    }
    
    const goToLogin = () => {
      router.push('/login')
    }
    
    const goToDataManagement = () => {
      router.push('/admin')
    }
    
    const goToJobSearch = () => {
      router.push('/jobs')
    }
    
    onMounted(() => {
      if (isLoggedIn.value) {
        loadUserInfo()
        loadRecommendations()
      }
    })
    
    return {
      isLoggedIn,
      userInfo,
      userAvatar,
      activeTab,
      recommendedJobs,
      recommendedSkills,
      showEditDialog,
      showSkillEdit,
      saving,
      savingSkills,
      editForm,
      skillInput,
      selectedSkills,
      allSkills,
      salaryRange,
      salaryComparison,
      salaryFactors,
      salaryAnalysis,
      loadRecommendations,
      saveProfile,
      saveSkills,
      removeSelectedSkill,
      removeSkill,
      getMatchColor,
      getImpactColor,
      goToLogin,
      goToDataManagement,
      goToJobSearch,
      generateLearningPath,
      initSkillEdit
    }
  }
}
</script>

<style scoped>
.dashboard-page {
  padding: 0;
}

.login-prompt {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 400px;
}

.profile-header {
  display: flex;
  align-items: center;
  margin-bottom: 20px;
}

.profile-info {
  margin-left: 15px;
}

.profile-info h3 {
  margin: 0 0 5px 0;
  font-size: 18px;
}

.profile-info p {
  margin: 0;
  color: #666;
}

.user-location {
  display: flex;
  align-items: center;
  gap: 5px;
  font-size: 14px;
}

.profile-stats {
  display: flex;
  justify-content: space-around;
  text-align: center;
  margin: 20px 0;
}

.stat-item {
  flex: 1;
}

.stat-value {
  font-size: 24px;
  font-weight: bold;
  color: #409EFF;
}

.stat-label {
  font-size: 12px;
  color: #666;
  margin-top: 5px;
}

.profile-actions {
  margin-top: 15px;
}

.skills-list {
  display: flex;
  flex-wrap: wrap;
}

.empty-skills {
  text-align: center;
  color: #999;
  padding: 20px;
}

.job-recommendation.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

.profile-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 15px;
}

.skills-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 10px;
}

.empty-skills {
  text-align: center;
  color: #999;
  padding: 20px 0;
}

.job-info h4 {
  margin: 0 0 5px 0;
}

.job-company {
  margin: 0 0 10px 0;
  color: #666;
}

.job-details {
  margin: 0;
}

.job-match {
  text-align: center;
  min-width: 100px;
}

.salary-value {
  font-size: 18px;
  font-weight: bold;
  color: #67c23a;
}

.text-success {
  color: #67c23a;
}

.text-warning {
  color: #e6a23c;
}

.text-danger {
  color: #f56c6c;
}

.skill-edit {
  padding: 10px 0;
}

.common-skills p {
  margin: 0 0 10px 0;
  font-size: 14px;
  color: #666;
}
</style>