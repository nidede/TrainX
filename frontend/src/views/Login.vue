<template>
  <div class="page-shell">
    <div class="page-grid">
      <section class="hero-panel">
        <div class="hero-badge">ICPC 级训练体系</div>
        <h1>欢迎来到 TRAINX</h1>
        <p>
          这是一个为高校算法竞赛准备的智能训练平台，覆盖 ICPC、CCPC、蓝桥杯、百度之星等多赛道内容。
        </p>
        <ul class="hero-features">
          <li>赛前指南与备赛策略</li>
          <li>知识库检索与题型分析</li>
          <li>个性化训练计划</li>
        </ul>
      </section>

      <div class="auth-card">
        <div class="card-header">
          <span class="icpc-tag">ICPC</span>
          <h2 class="card-title">TRAINX LOGIN</h2>
          <p class="card-subtitle">快速登录开始你的算法竞赛训练</p>
        </div>

        <div class="input-box">
          <input
            v-model="username"
            type="text"
            placeholder="USERNAME"
            class="icpc-input"
          />
        </div>

        <div class="input-box">
          <input
            v-model="password"
            type="password"
            placeholder="PASSWORD"
            class="icpc-input"
          />
        </div>

        <button @click="login" class="icpc-btn" :disabled="loading">
          <span v-if="loading">LOGGING IN...</span>
          <span v-else>LOGIN</span>
        </button>

        <div v-if="message" class="message-box" :class="messageType">
          {{ message }}
        </div>

        <div class="icpc-link">
          <span @click="goRegister">NO ACCOUNT? REGISTER</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import axios from 'axios'

const username = ref('')
const password = ref('')
const loading = ref(false)
const message = ref('')
const messageType = ref('')
const router = useRouter()
const route = useRoute()

const login = async () => {
  loading.value = true
  message.value = ''
  messageType.value = ''

  try {
    const res = await axios.post('/api/users/login/', {
      username: username.value,
      password: password.value
    })
    localStorage.setItem('trainx_token', res.data.token)
    localStorage.setItem('trainx_user', username.value)
    const redirect = route.query.redirect || '/home'
    router.push(redirect)
  } catch (err) {
    message.value = err.response?.data?.detail || '登录失败，请检查用户名和密码'
    messageType.value = 'error'
  } finally {
    loading.value = false
  }
}

const goRegister = () => {
  router.push('/register')
}
</script>

<style scoped>
.page-shell {
  min-height: 100vh;
  background: radial-gradient(circle at top left, #ffca28 0%, rgba(255, 202, 40, 0.18) 18%, transparent 26%),
    radial-gradient(circle at bottom right, #2962ff 0%, rgba(41, 98, 255, 0.24) 30%, transparent 50%),
    linear-gradient(180deg, #060812 0%, #09111e 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 40px;
  font-family: "Consolas", "Monaco", monospace;
}

.page-grid {
  display: grid;
  grid-template-columns: minmax(320px, 1.4fr) minmax(360px, 1fr);
  gap: 40px;
  width: min(1200px, 100%);
}

.hero-panel {
  color: #f8fafc;
  display: flex;
  flex-direction: column;
  justify-content: center;
  gap: 22px;
  padding: 40px 36px;
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 30px;
  background: rgba(255, 255, 255, 0.04);
  box-shadow: 0 30px 90px rgba(0, 0, 0, 0.25);
}

.hero-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: fit-content;
  padding: 10px 18px;
  border-radius: 999px;
  background: rgba(255, 82, 82, 0.18);
  color: #ffb3b3;
  letter-spacing: 1px;
  font-weight: 700;
}

.hero-panel h1 {
  margin: 0;
  font-size: clamp(2.5rem, 4vw, 4rem);
  line-height: 1.02;
}

.hero-panel p {
  max-width: 540px;
  color: #cbd5e1;
  font-size: 16px;
  line-height: 1.8;
}

.hero-features {
  list-style: none;
  padding: 0;
  display: grid;
  gap: 14px;
  margin: 0;
}

.hero-features li {
  display: flex;
  gap: 12px;
  align-items: center;
  color: #e2e8f0;
}

.hero-features li::before {
  content: '•';
  color: #ffca28;
}

.auth-card {
  background: rgba(6, 8, 18, 0.95);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 28px;
  padding: 42px 36px;
  box-shadow: 0 30px 90px rgba(0, 0, 0, 0.3);
}

.card-header {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-bottom: 32px;
}

.card-title {
  margin: 0;
  color: #f8fafc;
  font-size: 28px;
}

.card-subtitle {
  margin: 0;
  color: #94a3b8;
  font-size: 14px;
}

.input-box {
  margin-bottom: 18px;
}

.icpc-input {
  width: 100%;
  height: 50px;
  border-radius: 16px;
  border: 1px solid rgba(255, 255, 255, 0.12);
  padding: 0 18px;
  background: rgba(255, 255, 255, 0.04);
  color: #e2e8f0;
  outline: none;
  font-size: 14px;
}

.icpc-input::placeholder {
  color: #94a3b8;
}

.icpc-btn {
  width: 100%;
  height: 52px;
  border-radius: 16px;
  border: none;
  background: linear-gradient(135deg, #ffca28 0%, #2962ff 100%);
  color: #111827;
  font-size: 15px;
  font-weight: 800;
  letter-spacing: 1px;
  cursor: pointer;
  transition: transform 0.18s ease, box-shadow 0.18s ease;
}

.icpc-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 18px 30px rgba(41, 98, 255, 0.22);
}

.icpc-link {
  margin-top: 24px;
  text-align: center;
}

.icpc-link span {
  color: #82cfff;
  font-size: 13px;
  cursor: pointer;
  letter-spacing: 1px;
}

.icpc-link span:hover {
  color: #ffca28;
}

.message-box {
  margin-top: 18px;
  padding: 12px 14px;
  border-radius: 14px;
  font-size: 13px;
  line-height: 1.5;
}

.message-box.error {
  background: rgba(255, 82, 82, 0.12);
  color: #ffb3b3;
  border: 1px solid rgba(255, 82, 82, 0.28);
}

.icpc-btn:disabled {
  opacity: 0.65;
  cursor: not-allowed;
}

@media (max-width: 980px) {
  .page-grid {
    grid-template-columns: 1fr;
  }

  .hero-panel,
  .auth-card {
    padding: 28px 24px;
  }
}
</style>