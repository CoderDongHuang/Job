<template>
  <div class="login-container">
    <el-card class="login-card">
      <template #header>
        <div class="card-header">
          <h2>登录智析招聘</h2>
          <p>请输入您的账号信息</p>
        </div>
      </template>
      
      <el-form 
        :model="loginForm" 
        :rules="loginRules" 
        ref="loginFormRef"
        label-width="80px"
        @submit.prevent="handleLogin"
      >
        <el-form-item label="用户名" prop="username">
          <el-input 
            v-model="loginForm.username" 
            placeholder="请输入用户名"
            size="large"
            prefix-icon="User"
          />
        </el-form-item>
        
        <el-form-item label="密码" prop="password">
          <el-input 
            v-model="loginForm.password" 
            type="password"
            placeholder="请输入密码"
            size="large"
            prefix-icon="Lock"
            show-password
          />
        </el-form-item>
        
        <el-form-item>
          <el-button 
            type="primary" 
            size="large" 
            :loading="loading"
            @click="handleLogin"
            style="width: 100%;"
          >
            {{ loading ? '登录中...' : '登录' }}
          </el-button>
        </el-form-item>
        
        <div class="login-footer">
          <p>还没有账号？<el-link type="primary" @click="goToRegister">立即注册</el-link></p>
        </div>
      </el-form>
    </el-card>
    
    <!-- 演示账号提示 -->
    <el-card class="demo-accounts" style="margin-top: 20px;">
      <template #header>
        <div class="card-header">
          <h4>演示账号</h4>
        </div>
      </template>
      <div class="demo-account-list">
        <div v-for="account in demoAccounts" :key="account.username" class="demo-account">
          <p><strong>用户名:</strong> {{ account.username }}</p>
          <p><strong>密码:</strong> {{ account.password }}</p>
          <p><strong>职位:</strong> {{ account.title }}</p>
          <el-button size="small" @click="fillDemoAccount(account)">使用此账号</el-button>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import request from '@/utils/request'

export default {
  name: 'LoginView',
  setup() {
    const router = useRouter()
    const loginFormRef = ref()
    const loading = ref(false)
    
    const loginForm = reactive({
      username: '',
      password: ''
    })
    
    const loginRules = {
      username: [
        { required: true, message: '请输入用户名', trigger: 'blur' },
        { min: 3, max: 20, message: '用户名长度在 3 到 20 个字符', trigger: 'blur' }
      ],
      password: [
        { required: true, message: '请输入密码', trigger: 'blur' },
        { min: 6, message: '密码长度至少 6 个字符', trigger: 'blur' }
      ]
    }
    
    const demoAccounts = ref([
      { username: 'zhangsan', password: 'password123', title: '前端开发工程师' },
      { username: 'lisi', password: 'password123', title: 'Python开发工程师' },
      { username: 'wangwu', password: 'password123', title: '数据科学家' }
    ])
    
    const handleLogin = async () => {
      if (!loginFormRef.value) return
      
      try {
        const valid = await loginFormRef.value.validate()
        if (!valid) return
        
        loading.value = true
        
        const response = await request.post('/users/login', loginForm)
        
        if (response && response.access_token) {
          // 保存token到localStorage
          localStorage.setItem('token', response.access_token)
          localStorage.setItem('user', JSON.stringify(response.user))
          
          ElMessage.success('登录成功！')
          
          // 跳转到首页
          router.push('/')
        }
      } catch (error) {
        console.error('登录失败:', error)
        ElMessage.error('登录失败，请检查用户名和密码')
      } finally {
        loading.value = false
      }
    }
    
    const goToRegister = () => {
      router.push('/register')
    }
    
    const fillDemoAccount = (account) => {
      loginForm.username = account.username
      loginForm.password = account.password
    }
    
    return {
      loginFormRef,
      loginForm,
      loginRules,
      loading,
      demoAccounts,
      handleLogin,
      goToRegister,
      fillDemoAccount
    }
  }
}
</script>

<style scoped>
.login-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
}

.login-card {
  width: 400px;
  max-width: 90vw;
}

.card-header {
  text-align: center;
}

.card-header h2 {
  margin: 0 0 10px 0;
  color: #333;
}

.card-header p {
  margin: 0;
  color: #666;
  font-size: 14px;
}

.login-footer {
  text-align: center;
  margin-top: 20px;
}

.demo-accounts {
  width: 400px;
  max-width: 90vw;
}

.demo-account-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.demo-account {
  padding: 15px;
  border: 1px solid #e4e7ed;
  border-radius: 4px;
  background: #f8f9fa;
}

.demo-account p {
  margin: 5px 0;
  font-size: 14px;
}
</style>