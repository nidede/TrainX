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

// 全局响应拦截：401 自动跳转登录
axios.interceptors.response.use(
  response => response,
  error => {
    if (error.response && error.response.status === 401) {
      localStorage.removeItem('trainx_token')
      localStorage.removeItem('trainx_user')
      if (router.currentRoute.value.path !== '/login') {
        router.push({ path: '/login', query: { redirect: router.currentRoute.value.fullPath } })
      }
    }
    return Promise.reject(error)
  }
)

createApp(App).use(router).mount('#app')
