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
                <el-button type="primary" size="small" @click="showSkillEdit = true">编辑技能</el-button>
              </div>
            </template>
            
            <div v-if="userInfo.skills && userInfo.skills.length > 0" class="skills-list">
              <el-tag 
                v-for="skill in userInfo.skills" 
                :key="skill" 
                size="medium"
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
                  <h4>建议学习的技能</h4>
                  <el-table :data="recommendedSkills" style="width: 100%;">
                    <el-table-column prop="skill" label="技能" width="150">
                      <template #default="{ row }">
                        <el-tag>{{ row.skill }}</el-tag>
                      </template>
                    </el-table-column>
                    <el-table-column prop="importance" label="重要性" width="120">
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
                    <el-table-column prop="benefit" label="薪资提升" width="120">
                      <template #default="{ row }">
                        +{{ row.benefit }}%
                      </template>
                    </el-table-column>
                    <el-table-column prop="learningTime" label="学习周期" width="100">
                      <template #default="{ row }">
                        {{ row.learningTime }}月
                      </template>
                    </el-table-column>
                    <el-table-column label="操作">
                      <template #default="{ row }">
                        <el-button size="small" type="primary">学习计划</el-button>
                      </template>
                    </el-table-column>
                  </el-table>
                  
                  <h4 style="margin-top: 30px;">学习路径推荐</h4>
                  <el-steps :active="2" finish-status="success" align-center>
                    <el-step title="基础技能" description="HTML/CSS/JavaScript" />
                    <el-step title="框架学习" description="Vue.js/React" />
                    <el-step title="进阶技能" description="Node.js/数据库" />
                    <el-step title="项目实战" description="完整项目开发" />
                  </el-steps>
                </div>
              </el-tab-pane>
              
              <!-- 薪资评估 -->
              <el-tab-pane label="薪资评估" name="salary">
                <div class="salary-assessment">
                  <h4>当前市场价值评估</h4>
                  <div class="salary-range">
                    <p>预计薪资范围：<span class="salary-value">¥{{ (salaryRange.min/1000).toFixed(0) }}K - ¥{{ (salaryRange.max/1000).toFixed(0) }}K</span></p>
                    <p>相比当前薪资：<span :class="salaryComparison.class">{{ salaryComparison.text }}</span></p>
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
    <el-dialog v-model="showSkillEdit" title="编辑技能" width="500px">
      <div class="skill-edit">
        <p>请输入您的技能（每个技能用逗号分隔）：</p>
        <el-input
          v-model="skillInput"
          type="textarea"
          :rows="4"
          placeholder="例如：Python, JavaScript, Vue.js, MySQL, Docker"
        />
        <div class="common-skills" style="margin-top: 15px;">
          <p>常用技能：</p>
          <el-tag 
            v-for="skill in commonSkills" 
            :key="skill" 
            style="margin: 4px; cursor: pointer;"
            @click="addSkill(skill)"
          >
            {{ skill }}
          </el-tag>
        </div>
      </div>
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
    const commonSkills = ref([
      'Python', 'Java', 'JavaScript', 'TypeScript', 'Vue.js', 'React',
      'MySQL', 'Redis', 'Docker', 'Kubernetes', 'Git', 'Linux',
      '机器学习', '数据分析', '前端开发', '后端开发', 'DevOps'
    ])
    
    // 模拟数据
    const salaryRange = ref({ min: 15000, max: 25000 })
    const salaryComparison = ref({ class: 'text-success', text: '+25%' })
    const salaryFactors = ref([
      { factor: '技能匹配度', impact: 85, value: '良好' },
      { factor: '工作经验', impact: 70, value: '3年' },
      { factor: '学历背景', impact: 60, value: '本科' },
      { factor: '所在城市', impact: 80, value: '一线城市' }
    ])
    
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
      } catch (error) {
        console.error('加载用户信息失败:', error)
        ElMessage.error('加载用户信息失败')
      }
    }
    
    // 加载推荐数据
    const loadRecommendations = async () => {
      try {
        const response = await request.get('/users/me/recommendations')
        recommendedJobs.value = response.recommended_jobs || []
        recommendedSkills.value = response.recommendations || []
      } catch (error) {
        console.error('加载推荐数据失败:', error)
        // 使用模拟数据
        recommendedJobs.value = [
          { id: 1, title: '高级前端开发工程师', company: '阿里巴巴', city: '北京', salary_min: 20000, salary_max: 35000, experience_required: '3-5年' },
          { id: 2, title: '全栈开发工程师', company: '腾讯', city: '深圳', salary_min: 18000, salary_max: 30000, experience_required: '3-5年' }
        ]
        recommendedSkills.value = [
          { skill: 'TypeScript', importance: 4, benefit: 15, learningTime: 3 },
          { skill: 'Node.js', importance: 3, benefit: 12, learningTime: 4 },
          { skill: 'Docker', importance: 3, benefit: 10, learningTime: 2 }
        ]
      }
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
    
    // 保存技能
    const saveSkills = async () => {
      savingSkills.value = true
      try {
        const skills = skillInput.value.split(',').map(s => s.trim()).filter(s => s)
        await request.put('/users/me/skills', { skills })
        ElMessage.success('技能更新成功')
        showSkillEdit.value = false
        await loadUserInfo() // 重新加载用户信息
      } catch (error) {
        console.error('保存技能失败:', error)
        ElMessage.error('保存失败')
      } finally {
        savingSkills.value = false
      }
    }
    
    // 添加技能
    const addSkill = (skill) => {
      const skills = skillInput.value ? skillInput.value.split(',').map(s => s.trim()) : []
      if (!skills.includes(skill)) {
        skills.push(skill)
        skillInput.value = skills.join(', ')
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
      commonSkills,
      salaryRange,
      salaryComparison,
      salaryFactors,
      loadRecommendations,
      saveProfile,
      saveSkills,
      addSkill,
      getMatchColor,
      getImpactColor,
      goToLogin,
      goToDataManagement,
      goToJobSearch
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