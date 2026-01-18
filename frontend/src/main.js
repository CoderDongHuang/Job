import { createApp } from 'vue'
import { createPinia } from 'pinia'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import * as ElementPlusIconsVue from '@element-plus/icons-vue'

import App from './App.vue'
import router from './router'

const app = createApp(App)

// 注册所有图标
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component)
}

app.use(createPinia())
app.use(router)

// 配置Element Plus以减少警告
app.use(ElementPlus, {
  // 可以添加一些配置选项来减少警告
})

// 在开发模式下，可以配置Vue来忽略某些警告
if (import.meta.env.DEV) {
  // 临时解决方案：忽略插槽相关的警告
  const originalWarn = console.warn
  console.warn = (...args) => {
    if (args[0] && args[0].includes('Slot') && args[0].includes('invoked outside')) {
      return // 忽略插槽警告
    }
    originalWarn.apply(console, args)
  }
}

app.mount('#app')