import { createApp } from 'vue'
import './style.css'
import App from './App.vue'
import router from './router'
import axios from 'axios'
import { marked } from 'marked'
import katex from 'katex'

// ── 全局 Markdown 配置 ──
marked.use({ gfm: true, breaks: true })

// 自定义渲染器：用 KaTeX 渲染 LaTeX
const renderer = new marked.Renderer()
const origCode = renderer.code.bind(renderer)
renderer.code = function (obj) {
  // marked v18 code handler receives object
  if (typeof obj === 'object' && obj.lang === 'math') {
    try { return katex.renderToString(obj.text, { displayMode: true, throwOnError: false }) } catch { return `<code>${obj.text}</code>` }
  }
  return typeof obj === 'object' ? origCode(obj) : origCode(...arguments)
}

// 在 Markdown 渲染前先处理 LaTeX
window.renderMarkdown = function (text) {
  if (!text) return ''
  // 块级公式 $...$
  text = text.replace(/\$\$([\s\S]*?)\$\$/g, (m, formula) => {
    try { return katex.renderToString(formula.trim(), { displayMode: true, throwOnError: false }) } catch { return m }
  })
  // 行内公式 $...$（不匹配 $）
  text = text.replace(/(?<!\$)\$(?!\$)(.*?)\$(?!\$)/g, (m, formula) => {
    try { return katex.renderToString(formula.trim(), { displayMode: false, throwOnError: false }) } catch { return m }
  })
  return marked(text, { renderer })
}

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
