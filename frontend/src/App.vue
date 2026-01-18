<template>
  <div id="app">
    <el-container>
      <el-header>
        <div class="header-content">
          <div class="logo">
            <h2>智析招聘</h2>
          </div>
          <el-menu
            :default-active="activeIndex"
            mode="horizontal"
            @select="handleSelect"
            router
          >
            <el-menu-item index="/">首页</el-menu-item>
            <el-menu-item index="/jobs">职位搜索</el-menu-item>
            <el-menu-item index="/skills">技能分析</el-menu-item>
            <el-menu-item index="/analysis">数据分析</el-menu-item>
            <el-menu-item index="/dashboard">个人中心</el-menu-item>
          </el-menu>
          <div class="user-info">
            <template v-if="isLoggedIn">
              <el-dropdown @command="handleUserCommand">
                <span class="user-dropdown">
                  <el-avatar :size="32" :src="userAvatar" />
                  <span class="username">{{ userInfo?.fullName || userInfo?.username }}</span>
                  <el-icon><ArrowDown /></el-icon>
                </span>
                <template #dropdown>
                  <el-dropdown-menu>
              <el-dropdown-item command="profile">个人资料</el-dropdown-item>
              <el-dropdown-item command="admin">数据管理</el-dropdown-item>
              <el-dropdown-item command="logout">退出登录</el-dropdown-item>
            </el-dropdown-menu>
                </template>
              </el-dropdown>
            </template>
            <template v-else>
              <el-button type="primary" @click="goToLogin" size="small">登录</el-button>
              <el-button @click="goToRegister" size="small">注册</el-button>
            </template>
          </div>
        </div>
      </el-header>
      
      <el-main>
        <router-view />
      </el-main>
      
      <el-footer>
        <div class="footer-content">
          <p>© 2026 智析招聘 - 招聘数据分析与技能洞察系统</p>
          <p>由胡栋煌、孙志文、贺超超、刘兆栋联合打造</p>
        </div>
      </el-footer>
    </el-container>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { ArrowDown } from '@element-plus/icons-vue'
import request from '@/utils/request'

export default {
  name: 'App',
  components: {
    ArrowDown
  },
  setup() {
    const router = useRouter()
    const activeIndex = ref('/')
    
    // 用户认证状态
    const userInfo = ref(null)
    const isLoggedIn = computed(() => {
      return !!userInfo.value && !!localStorage.getItem('token')
    })
    
    const userAvatar = computed(() => {
      // 简单的头像生成，可以根据用户名生成默认头像
      return `https://api.dicebear.com/7.x/avataaars/svg?seed=${userInfo.value?.username || 'user'}`
    })
    
    // 检查用户登录状态
    const checkAuthStatus = () => {
      const token = localStorage.getItem('token')
      const userData = localStorage.getItem('user')
      
      if (token && userData) {
        try {
          userInfo.value = JSON.parse(userData)
        } catch (error) {
          console.error('解析用户数据失败:', error)
          logout()
        }
      }
    }
    
    // 用户命令处理
    const handleUserCommand = (command) => {
      switch (command) {
        case 'profile':
          router.push('/dashboard')
          break
        case 'admin':
          router.push('/admin')
          break
        case 'logout':
          logout()
          break
      }
    }
    
    // 退出登录
    const logout = () => {
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      userInfo.value = null
      ElMessage.success('已退出登录')
      router.push('/')
    }
    
    // 导航处理
    const handleSelect = (key) => {
      activeIndex.value = key
    }
    
    // 跳转到登录/注册
    const goToLogin = () => {
      router.push('/login')
    }
    
    const goToRegister = () => {
      router.push('/register')
    }
    
    onMounted(() => {
      // 设置当前激活菜单项
      activeIndex.value = router.currentRoute.value.path
      
      // 检查登录状态
      checkAuthStatus()
    })
    
    return {
      activeIndex,
      userInfo,
      isLoggedIn,
      userAvatar,
      handleSelect,
      handleUserCommand,
      goToLogin,
      goToRegister
    }
  }
}
</script>

<style>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  color: #2c3e50;
  height: 100vh;
}

.el-header {
  background-color: #409EFF;
  color: #fff;
  line-height: 60px;
  padding: 0 20px;
}

.header-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 100%;
}

.logo h2 {
  margin: 0;
  color: #fff;
  font-size: 24px;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 10px;
}

.user-dropdown {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  color: #fff;
  padding: 5px 10px;
  border-radius: 4px;
  transition: background-color 0.3s;
}

.user-dropdown:hover {
  background-color: rgba(255, 255, 255, 0.1);
}

.username {
  font-weight: 500;
}

.el-footer {
  background-color: #f5f5f5;
  color: #666;
  text-align: center;
  padding: 20px 0;
}

.el-main {
  background-color: #f0f2f5;
  padding: 20px;
  min-height: calc(100vh - 120px);
}

.footer-content p {
  margin: 5px 0;
}

body {
  margin: 0;
  padding: 0;
  height: 100%;
}
</style>