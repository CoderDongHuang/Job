<template>
  <div class="jobs-page">
    <el-row :gutter="20">
      <el-col :span="6">
        <el-card class="filter-panel">
          <h3>筛选条件</h3>
          <el-form label-position="top">
            <el-form-item label="城市">
              <el-select v-model="filters.city" placeholder="请选择城市" clearable>
                <el-option label="北京" value="北京"></el-option>
                <el-option label="上海" value="上海"></el-option>
                <el-option label="广州" value="广州"></el-option>
                <el-option label="深圳" value="深圳"></el-option>
                <el-option label="杭州" value="杭州"></el-option>
                <el-option label="成都" value="成都"></el-option>
              </el-select>
            </el-form-item>
            
            <el-form-item label="薪资范围">
              <el-slider
                v-model="salaryRange"
                range
                :min="0"
                :max="50000"
                :step="1000"
                :format-tooltip="formatSalaryTooltip"
              ></el-slider>
              <div class="salary-display">{{ salaryRange[0] }} - {{ salaryRange[1] }}</div>
            </el-form-item>
            
            <el-form-item label="工作经验">
              <el-select v-model="filters.experience" placeholder="请选择经验要求" clearable>
                <el-option label="应届毕业生" value="应届毕业生"></el-option>
                <el-option label="1年以内" value="1年以内"></el-option>
                <el-option label="1-3年" value="1-3年"></el-option>
                <el-option label="3-5年" value="3-5年"></el-option>
                <el-option label="5-10年" value="5-10年"></el-option>
                <el-option label="10年以上" value="10年以上"></el-option>
              </el-select>
            </el-form-item>
            
            <el-form-item label="学历要求">
              <el-select v-model="filters.education" placeholder="请选择学历要求" clearable>
                <el-option label="大专" value="大专"></el-option>
                <el-option label="本科" value="本科"></el-option>
                <el-option label="硕士" value="硕士"></el-option>
                <el-option label="博士" value="博士"></el-option>
              </el-select>
            </el-form-item>
            
            <el-button type="primary" @click="applyFilters" style="width: 100%;">应用筛选</el-button>
          </el-form>
        </el-card>
      </el-col>
      
      <el-col :span="18">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>职位列表</span>
              <el-input
                v-model="searchQuery"
                placeholder="搜索职位、公司或关键词"
                style="width: 300px;"
                @keyup.enter="searchJobs"
              >
                <template #suffix>
                  <el-icon @click="searchJobs"><Search /></el-icon>
                </template>
              </el-input>
            </div>
          </template>
          
          <el-table
            :data="jobs"
            style="width: 100%"
            v-loading="loading"
            row-key="id"
          >
            <el-table-column prop="title" label="职位名称" width="200">
              <template #default="{ row }">
                <div class="job-title">
                  <span>{{ row.title }}</span>
                  <el-tag size="small" type="info" style="margin-left: 10px;">{{ row.category }}</el-tag>
                </div>
              </template>
            </el-table-column>
            
            <el-table-column prop="company" label="公司" width="150"></el-table-column>
            
            <el-table-column prop="city" label="城市" width="100"></el-table-column>
            
            <el-table-column label="薪资" width="150">
              <template #default="{ row }">
                <div class="salary-cell">
                  <span class="salary-range">{{ formatSalary(row.salary_min, row.salary_max) }}</span>
                </div>
              </template>
            </el-table-column>
            
            <el-table-column prop="experience_required" label="经验要求" width="120"></el-table-column>
            
            <el-table-column prop="education_required" label="学历要求" width="120"></el-table-column>
            
            <el-table-column label="技能标签" width="200">
              <template #default="{ row }">
                <el-space wrap :size="4">
                  <el-tag 
                    v-for="tag in row.tags.slice(0, 3)" 
                    :key="tag" 
                    size="small"
                  >
                    {{ tag }}
                  </el-tag>
                  <el-popover
                    v-if="row.tags.length > 3"
                    placement="top-start"
                    :title="'全部技能标签 (' + row.tags.length + ')'"
                    trigger="hover"
                  >
                    <template #reference>
                      <el-tag size="small">+{{ row.tags.length - 3 }}</el-tag>
                    </template>
                    <div>
                      <el-tag 
                        v-for="tag in row.tags" 
                        :key="tag" 
                        size="small" 
                        style="margin: 2px;"
                      >
                        {{ tag }}
                      </el-tag>
                    </div>
                  </el-popover>
                </el-space>
              </template>
            </el-table-column>
            
            <el-table-column label="操作" width="150">
              <template #default="{ row }">
                <el-button size="small" @click="viewJobDetails(row)">详情</el-button>
              </template>
            </el-table-column>
          </el-table>
          
          <div class="pagination-container">
            <el-pagination
              @size-change="handleSizeChange"
              @current-change="handleCurrentChange"
              :current-page="currentPage"
              :page-sizes="[10, 20, 50, 100]"
              :page-size="pageSize"
              layout="total, sizes, prev, pager, next, jumper"
              :total="totalJobs"
            />
          </div>
        </el-card>
      </el-col>
    </el-row>
    
    <!-- 职位详情对话框 -->
    <el-dialog v-model="showJobDetail" title="职位详情" width="60%">
      <div v-if="selectedJob">
        <h3>{{ selectedJob.title }}</h3>
        <p><strong>公司：</strong>{{ selectedJob.company }}</p>
        <p><strong>城市：</strong>{{ selectedJob.city }}</p>
        <p><strong>薪资：</strong>{{ formatSalary(selectedJob.salary_min, selectedJob.salary_max) }}</p>
        <p><strong>经验要求：</strong>{{ selectedJob.experience_required }}</p>
        <p><strong>学历要求：</strong>{{ selectedJob.education_required }}</p>
        
        <h4>职位描述</h4>
        <p>{{ selectedJob.description }}</p>
        
        <h4>职位要求</h4>
        <p>{{ selectedJob.requirements }}</p>
        
        <h4>技能标签</h4>
        <el-space wrap :size="4">
          <el-tag 
            v-for="tag in selectedJob.tags" 
            :key="tag" 
            size="small"
          >
            {{ tag }}
          </el-tag>
        </el-space>
      </div>
    </el-dialog>
  </div>
</template>

<script>
import { ref, reactive, onMounted } from 'vue'
import { Search } from '@element-plus/icons-vue'
import request from '@/utils/request'
import { ElMessage } from 'element-plus'

export default {
  name: 'JobsView',
  setup() {
    // 数据
    const jobs = ref([])
    const loading = ref(false)
    const currentPage = ref(1)
    const pageSize = ref(10)
    const totalJobs = ref(0)
    const searchQuery = ref('')
    const showJobDetail = ref(false)
    const selectedJob = ref(null)
    
    // 筛选条件
    const filters = reactive({
      city: '',
      experience: '',
      education: ''
    })
    
    const salaryRange = ref([0, 50000])
    
    // 方法
    const loadJobs = async () => {
      loading.value = true
      try {
        // 构建查询参数
        const params = {
          skip: (currentPage.value - 1) * pageSize.value,
          limit: pageSize.value,
        }
        
        // 关键词搜索
        if (searchQuery.value) {
          params.keyword = searchQuery.value
        }
        
        // 城市筛选
        if (filters.city) {
          params.city = filters.city
        }
        
        // 薪资范围筛选
        if (salaryRange.value[0] > 0 || salaryRange.value[1] < 50000) {
          params.salary_min = salaryRange.value[0]
          params.salary_max = salaryRange.value[1]
        }
        
        // 经验要求筛选
        if (filters.experience) {
          params.experience = filters.experience
        }
        
        // 学历要求筛选
        if (filters.education) {
          params.education = filters.education
        }
        
        // 真实API调用
        const response = await request.get('/jobs', { params })
        jobs.value = Array.isArray(response) ? response : []
        totalJobs.value = 1000 // 后续可扩展为从API获取实际总数
      } catch (error) {
        console.error('加载职位失败:', error)
        ElMessage.error('加载职位失败，请稍后重试')
      } finally {
        loading.value = false
      }
    }
    
    const formatSalary = (min, max) => {
      return `${(min/1000).toFixed(0)}K-${(max/1000).toFixed(0)}K/月`
    }
    
    const formatSalaryTooltip = (value) => {
      return `${(value/1000).toFixed(0)}K`
    }
    
    const applyFilters = () => {
      currentPage.value = 1
      loadJobs()
    }
    
    const searchJobs = () => {
      currentPage.value = 1
      loadJobs()
    }
    
    const handleSizeChange = (size) => {
      pageSize.value = size
      currentPage.value = 1
      loadJobs()
    }
    
    const handleCurrentChange = (page) => {
      currentPage.value = page
      loadJobs()
    }
    
    const viewJobDetails = (job) => {
      selectedJob.value = job
      showJobDetail.value = true
    }
    
    // 初始化
    onMounted(() => {
      loadJobs()
    })
    
    return {
      jobs,
      loading,
      currentPage,
      pageSize,
      totalJobs,
      searchQuery,
      showJobDetail,
      selectedJob,
      filters,
      salaryRange,
      loadJobs,
      formatSalary,
      formatSalaryTooltip,
      applyFilters,
      searchJobs,
      handleSizeChange,
      handleCurrentChange,
      viewJobDetails,
      Search
    }
  }
}
</script>

<style scoped>
.jobs-page {
  padding: 20px;
}

.filter-panel {
  height: fit-content;
  position: sticky;
  top: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.job-title {
  display: flex;
  align-items: center;
}

.salary-cell {
  display: flex;
  align-items: center;
}

.salary-range {
  font-weight: bold;
  color: #e6a23c;
}

.pagination-container {
  margin-top: 20px;
  text-align: center;
}

.el-tag + .el-tag {
  margin-left: 4px;
}
</style>