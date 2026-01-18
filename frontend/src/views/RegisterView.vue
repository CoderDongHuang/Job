<template>
  <div class="register-container">
    <el-card class="register-card">
      <template #header>
        <div class="card-header">
          <h2>注册智析招聘账号</h2>
          <p>创建您的个人账号</p>
        </div>
      </template>
      
      <el-form 
        :model="registerForm" 
        :rules="registerRules" 
        ref="registerFormRef"
        label-width="100px"
        @submit.prevent="handleRegister"
      >
        <el-form-item label="用户名" prop="username">
          <el-input 
            v-model="registerForm.username" 
            placeholder="请输入用户名（3-20位）"
            size="large"
            prefix-icon="User"
          />
        </el-form-item>
        
        <el-form-item label="邮箱" prop="email">
          <el-input 
            v-model="registerForm.email" 
            placeholder="请输入邮箱地址"
            size="large"
            prefix-icon="Message"
          />
        </el-form-item>
        
        <el-form-item label="密码" prop="password">
          <el-input 
            v-model="registerForm.password" 
            type="password"
            placeholder="请输入密码（至少6位）"
            size="large"
            prefix-icon="Lock"
            show-password
          />
        </el-form-item>
        
        <el-form-item label="确认密码" prop="confirmPassword">
          <el-input 
            v-model="registerForm.confirmPassword" 
            type="password"
            placeholder="请再次输入密码"
            size="large"
            prefix-icon="Lock"
            show-password
          />
        </el-form-item>
        
        <el-form-item label="姓名" prop="fullName">
          <el-input 
            v-model="registerForm.fullName" 
            placeholder="请输入真实姓名"
            size="large"
          />
        </el-form-item>
        
        <el-form-item label="职位" prop="title">
          <el-input 
            v-model="registerForm.title" 
            placeholder="如：前端开发工程师"
            size="large"
          />
        </el-form-item>
        
        <el-form-item>
          <el-button 
            type="primary" 
            size="large" 
            :loading="loading"
            @click="handleRegister"
            style="width: 100%;"
          >
            {{ loading ? '注册中...' : '注册' }}
          </el-button>
        </el-form-item>
        
        <div class="register-footer">
          <p>已有账号？<el-link type="primary" @click="goToLogin">立即登录</el-link></p>
        </div>
      </el-form>
    </el-card>
  </div>
</template>

<script>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import request from '@/utils/request'

export default {
  name: 'RegisterView',
  setup() {
    const router = useRouter()
    const registerFormRef = ref()
    const loading = ref(false)
    
    const registerForm = reactive({
      username: '',
      email: '',
      password: '',
      confirmPassword: '',
      fullName: '',
      title: ''
    })
    
    const validatePassword = (rule, value, callback) => {
      if (value === '') {
        callback(new Error('请再次输入密码'))
      } else if (value !== registerForm.password) {
        callback(new Error('两次输入密码不一致'))
      } else {
        callback()
      }
    }
    
    const registerRules = {
      username: [
        { required: true, message: '请输入用户名', trigger: 'blur' },
        { min: 3, max: 20, message: '用户名长度在 3 到 20 个字符', trigger: 'blur' }
      ],
      email: [
        { required: true, message: '请输入邮箱地址', trigger: 'blur' },
        { type: 'email', message: '请输入正确的邮箱地址', trigger: 'blur' }
      ],
      password: [
        { required: true, message: '请输入密码', trigger: 'blur' },
        { min: 6, message: '密码长度至少 6 个字符', trigger: 'blur' }
      ],
      confirmPassword: [
        { required: true, message: '请再次输入密码', trigger: 'blur' },
        { validator: validatePassword, trigger: 'blur' }
      ],
      fullName: [
        { required: true, message: '请输入姓名', trigger: 'blur' }
      ],
      title: [
        { required: true, message: '请输入职位', trigger: 'blur' }
      ]
    }
    
    const handleRegister = async () => {
      if (!registerFormRef.value) return
      
      try {
        const valid = await registerFormRef.value.validate()
        if (!valid) return
        
        loading.value = true
        
        // 准备注册数据
        const registerData = {
          username: registerForm.username,
          email: registerForm.email,
          password: registerForm.password,
          fullName: registerForm.fullName,
          title: registerForm.title
        }
        
        const response = await request.post('/users/register', registerData)
        
        if (response) {
          ElMessage.success('注册成功！请登录')
          
          // 跳转到登录页面
          router.push('/login')
        }
      } catch (error) {
        console.error('注册失败:', error)
        ElMessage.error('注册失败：' + (error.response?.data?.detail || '请检查输入信息'))
      } finally {
        loading.value = false
      }
    }
    
    const goToLogin = () => {
      router.push('/login')
    }
    
    return {
      registerFormRef,
      registerForm,
      registerRules,
      loading,
      handleRegister,
      goToLogin
    }
  }
}
</script>

<style scoped>
.register-container {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
}

.register-card {
  width: 500px;
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

.register-footer {
  text-align: center;
  margin-top: 20px;
}
</style>