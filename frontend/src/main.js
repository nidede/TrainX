import { createApp } from 'vue'
import './style.css'
import App from './App.vue'
import router from './router'
import axios from 'axios'

// 全局设置：每次请求自动带上 Token
axios.interceptors.request.use(config => {
  const token = localStorage.getItem('trainx_token')
  if (token) {
    config.headers.Authorization = `Token ${token}`
  }
  return config
})

createApp(App).use(router).mount('#app')
