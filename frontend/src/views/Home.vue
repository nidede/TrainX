<template>
  <div class="home-page">
    <header class="home-header">
      <div class="logo-block">
        <div class="brand-mark">T</div>
        <div>
          <div class="brand-name">TRAINX</div>
          <div class="brand-subtitle">多赛事协同训练平台</div>
        </div>
      </div>
      <nav>
        <template v-if="!username">
          <router-link to="/login">登录</router-link>
          <router-link to="/register">注册</router-link>
        </template>
        <template v-else>
          <router-link to="/user-center" class="user-center-link">{{ username }}</router-link>
          <button class="logout-btn" @click="logout">退出</button>
        </template>
      </nav>
    </header>

    <section class="hero-panel">
      <div class="hero-copy">
        <span class="hero-label">ICPC 级训练体系</span>
        <h1 v-if="username">欢迎回来，{{ username }}</h1>
        <h1 v-else>覆盖算法、工程与创新的智能备赛平台</h1>
        <p>
          <template v-if="username">
            继续在 TRAINX 上展开你的竞赛备战，覆盖 ICPC、CCPC、蓝桥杯、百度之星等多赛道训练内容。
          </template>
          <template v-else>
            集成赛前指南、知识库检索与个性化训练计划，帮助学生在 ICPC、CCPC、蓝桥杯、百度之星等
            多赛道竞赛中高效提升实战能力。
          </template>
        </p>
        <div class="hero-actions">
          <router-link v-if="!username" to="/login" class="hero-btn">立即登录</router-link>
          <router-link v-if="!username" to="/register" class="hero-btn hero-btn-secondary">快速注册</router-link>
          <button v-else class="hero-btn" @click="continueLearning">开始训练</button>
        </div>
      </div>
      <div class="hero-stats">
        <router-link to="/six-tracks" class="hero-card yellow hero-card-link">
          <div class="hero-card-title">六大赛道</div>
          <p>覆盖算法竞技、工程实践、综合创新等核心能力。</p>
        </router-link>
        <router-link to="/problems" class="hero-card blue hero-card-link">
          <div class="hero-card-title">结构化知识库</div>
          <p>题型、知识点、实战经验一键检索。</p>
        </router-link>
        <router-link to="/training-plan" class="hero-card red hero-card-link">
          <div class="hero-card-title">智能训练</div>
          <p>生成个性化赛前计划，助力备战效率最大化。</p>
        </router-link>
        <router-link to="/blog" class="hero-card green hero-card-link">
          <div class="hero-card-title">竞赛博客</div>
          <p>分享备赛经验、题解心得，与社区交流成长。</p>
        </router-link>
      </div>
    </section>

    <section class="overview-section">
      <h2>你的竞赛训练新入口</h2>
      <div class="overview-grid">
        <article>
          <h3>精准赛前指南</h3>
          <p>分类汇总 ICPC、蓝桥杯、百度之星等赛事规则、题型和备赛策略。</p>
        </article>
        <article>
          <h3>知识点导航</h3>
          <p>结构化知识库支持按主题、难度、赛道查找关键知识节点。</p>
        </article>
        <article>
          <h3>训练计划</h3>
          <p>根据你的目标、时间和赛程，自动推荐训练任务。</p>
        </article>
      </div>
    </section>

    <footer class="home-footer">
      <span>TrainX · 竞赛训练助手</span>
      <span>专注高校竞赛人才培养与实战能力提升</span>
    </footer>

    <!-- AI 悬浮球 + 聊天面板 -->
    <div :class="['ai-fab', { 'ai-fab--active': chatOpen }]" @click="chatOpen = !chatOpen">
      <span v-if="!chatOpen" class="ai-fab-icon">AI</span>
      <span v-else class="ai-fab-icon">&times;</span>
    </div>

    <div v-if="chatOpen" class="ai-chat-panel">
      <div class="ai-chat-header">
        <span>AI 训练助手</span>
        <button class="ai-chat-close" @click="chatOpen = false">&times;</button>
      </div>
      <div class="ai-chat-messages" ref="chatMessagesRef">
        <div v-if="chatMessages.length === 0" class="ai-chat-welcome">
          你好！我是 TrainX AI 助手，可以帮你解答算法问题、制定训练计划。
        </div>
        <div v-for="(msg, i) in chatMessages" :key="i" :class="['ai-chat-msg', `ai-chat-msg--${msg.role}`]">
          <div class="ai-chat-msg-text">{{ msg.content }}</div>
        </div>
        <div v-if="chatLoading" class="ai-chat-msg ai-chat-msg--assistant">
          <div class="ai-chat-msg-text ai-typing">思考中…</div>
        </div>
      </div>
      <div class="ai-chat-input-bar">
        <input
          v-model="chatInput"
          placeholder="输入问题…"
          class="ai-chat-input"
          @keydown.enter="sendMessage"
          :disabled="chatLoading"
        />
        <button class="ai-chat-send" :disabled="!chatInput.trim() || chatLoading" @click="sendMessage">发送</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'

const username = ref('')
const router = useRouter()

onMounted(() => {
  username.value = localStorage.getItem('trainx_user') || ''
})

const logout = () => {
  localStorage.removeItem('trainx_user')
  username.value = ''
  router.push('/login')
}

const continueLearning = () => {
  router.push('/training-plan')
}

// ── AI 聊天 ──
const chatOpen = ref(false)
const chatInput = ref('')
const chatLoading = ref(false)
const chatMessages = ref([])
const chatMessagesRef = ref(null)
const conversationId = ref('')

async function sendMessage() {
  const text = chatInput.value.trim()
  if (!text || chatLoading.value) return
  chatMessages.value.push({ role: 'user', content: text })
  chatInput.value = ''
  chatLoading.value = true
  await nextTick()
  scrollToBottom()

  try {
    const res = await axios.post('/api/users/coze-chat/', {
      message: text,
      conversation_id: conversationId.value,
    })
    conversationId.value = res.data.conversation_id || ''
    chatMessages.value.push({ role: 'assistant', content: res.data.answer })
  } catch (e) {
    chatMessages.value.push({ role: 'assistant', content: '抱歉，AI 助手暂时无法回复，请稍后再试。' })
  } finally {
    chatLoading.value = false
    await nextTick()
    scrollToBottom()
  }
}

function scrollToBottom() {
  if (chatMessagesRef.value) {
    chatMessagesRef.value.scrollTop = chatMessagesRef.value.scrollHeight
  }
}
</script>

<style scoped>
.home-page {
  min-height: 100vh;
  background: radial-gradient(circle at top left, rgba(255, 202, 40, 0.16), transparent 30%),
    radial-gradient(circle at right, rgba(41, 98, 255, 0.18), transparent 25%),
    linear-gradient(180deg, #060812 0%, #09111e 100%);
  color: #f8fafc;
  padding: 32px 0;
  font-family: "Consolas", "Monaco", monospace;
}
.home-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 20px;
  max-width: 1400px;
  margin: 0 auto 40px;
  padding: 18px 48px;
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 24px;
  backdrop-filter: blur(12px);
}

.logo-block {
  display: flex;
  align-items: center;
  gap: 14px;
}

.brand-mark {
  width: 52px;
  height: 52px;
  border-radius: 18px;
  display: grid;
  place-items: center;
  background: linear-gradient(135deg, #ffca28, #ff5252);
  color: #111827;
  font-weight: 800;
  font-size: 24px;
}

.brand-name {
  font-size: 20px;
  font-weight: 800;
}

.brand-subtitle {
  margin-top: 2px;
  color: #94a3b8;
  font-size: 14px;
}

.home-header nav {
  display: flex;
  gap: 18px;
}

.home-header a {
  color: #f8fafc;
  text-decoration: none;
  font-weight: 600;
  padding: 10px 18px;
  border-radius: 14px;
  transition: background 0.2s ease;
}

.home-header a:hover {
  background: rgba(255, 255, 255, 0.08);
}

.user-center-link {
  color: #f8fafc;
  text-decoration: none;
  font-weight: 600;
  padding: 10px 18px;
  border-radius: 14px;
  transition: background 0.2s ease;
}

.user-center-link:hover {
  background: rgba(255, 255, 255, 0.08);
}

.hero-panel {
  display: grid;
  grid-template-columns: 1.3fr 1fr;
  gap: 28px;
  align-items: center;
  margin: 0 auto 40px;
  max-width: 1400px;
  padding: 0 48px;
}

.hero-copy {
  max-width: 600px;
}

.hero-label {
  display: inline-block;
  padding: 8px 16px;
  border-radius: 999px;
  background: rgba(255, 202, 40, 0.2);
  color: #ffca28;
  font-weight: 700;
  letter-spacing: 1px;
  margin-bottom: 18px;
}

.hero-copy h1 {
  font-size: 46px;
  line-height: 1.05;
  margin: 0 0 20px;
}

.hero-copy p {
  max-width: 600px;
  color: #cbd5e1;
  line-height: 1.8;
  margin-bottom: 30px;
}

.hero-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 14px;
}

.hero-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 160px;
  padding: 14px 24px;
  border-radius: 16px;
  background: linear-gradient(135deg, #ffca28 0%, #ff5252 45%, #2962ff 100%);
  color: #111827;
  font-weight: 700;
  text-decoration: none;
}

.hero-btn-secondary {
  background: rgba(255, 255, 255, 0.08);
  color: #f8fafc;
}

.hero-stats {
  display: grid;
  gap: 18px;
}

.hero-card {
  padding: 26px;
  border-radius: 24px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.08);
  min-height: 150px;
}

.hero-card-title {
  color: #ffffff;
  font-weight: 700;
  margin-bottom: 12px;
}

.hero-card p {
  color: #cbd5e1;
  line-height: 1.8;
}

.hero-card.yellow {
  border-color: rgba(255, 202, 40, 0.35);
}

.hero-card-link {
  display: block;
  color: inherit;
  text-decoration: none;
}

.hero-card-link:hover {
  background: rgba(255, 255, 255, 0.1);
}

.hero-card.blue {
  border-color: rgba(41, 98, 255, 0.35);
}

.hero-card.red {
  border-color: rgba(255, 82, 82, 0.35);
}

.hero-card.green {
  border-color: rgba(74, 222, 128, 0.35);
}

.overview-section {
  padding: 36px;
  border-radius: 28px;
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(255, 255, 255, 0.08);
  max-width: 1200px;
  margin: 0 auto;
}

.overview-section h2 {
  margin: 0 0 24px;
  font-size: 28px;
}

.overview-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 18px;
}

.overview-grid article {
  padding: 24px;
  border-radius: 20px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.08);
}

.overview-grid h3 {
  margin-top: 0;
  color: #ffffff;
}

.overview-grid p {
  color: #cbd5e1;
  margin: 8px 0 0;
  line-height: 1.75;
}

.home-footer {
  margin-top: 40px;
  display: flex;
  justify-content: space-between;
  gap: 20px;
  color: #94a3b8;
  font-size: 14px;
  max-width: 1200px;
  margin-left: auto;
  margin-right: auto;
}

/* ── AI 悬浮球 ── */
.ai-fab {
  position: fixed;
  bottom: 28px;
  right: 28px;
  width: 52px;
  height: 52px;
  border-radius: 50%;
  background: linear-gradient(135deg, #ffca28, #2962ff);
  color: #111827;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  box-shadow: 0 4px 20px rgba(41, 98, 255, 0.35);
  z-index: 1000;
  transition: all 0.25s ease;
  user-select: none;
}
.ai-fab:hover { transform: scale(1.1); }
.ai-fab--active {
  background: rgba(255,255,255,0.12);
  color: #fff;
  box-shadow: none;
}
.ai-fab-icon {
  font-size: 16px;
  font-weight: 800;
  line-height: 1;
}

/* ── AI 聊天面板 ── */
.ai-chat-panel {
  position: fixed;
  bottom: 92px;
  right: 28px;
  width: 380px;
  height: 520px;
  border-radius: 16px;
  background: #111827;
  border: 1px solid rgba(255,255,255,0.1);
  box-shadow: 0 16px 48px rgba(0,0,0,0.6);
  display: flex;
  flex-direction: column;
  z-index: 1001;
  overflow: hidden;
}
.ai-chat-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 14px 18px;
  background: rgba(255,255,255,0.04);
  border-bottom: 1px solid rgba(255,255,255,0.06);
  font-weight: 700;
  font-size: 15px;
  color: #e2e8f0;
}
.ai-chat-close {
  background: none;
  border: none;
  color: #64748b;
  font-size: 20px;
  cursor: pointer;
  line-height: 1;
}
.ai-chat-close:hover { color: #fff; }
.ai-chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 10px;
}
.ai-chat-welcome {
  text-align: center;
  color: #64748b;
  font-size: 13px;
  padding: 20px 10px;
  line-height: 1.6;
}
.ai-chat-msg {
  max-width: 85%;
}
.ai-chat-msg--user {
  align-self: flex-end;
}
.ai-chat-msg--assistant {
  align-self: flex-start;
}
.ai-chat-msg-text {
  padding: 10px 14px;
  border-radius: 12px;
  font-size: 14px;
  line-height: 1.6;
  white-space: pre-wrap;
  word-break: break-word;
}
.ai-chat-msg--user .ai-chat-msg-text {
  background: linear-gradient(135deg, #2962ff, #1e40af);
  color: #fff;
  border-bottom-right-radius: 4px;
}
.ai-chat-msg--assistant .ai-chat-msg-text {
  background: rgba(255,255,255,0.06);
  color: #e2e8f0;
  border-bottom-left-radius: 4px;
}
.ai-typing {
  color: #64748b;
  font-style: italic;
}
.ai-chat-input-bar {
  display: flex;
  gap: 8px;
  padding: 12px 14px;
  border-top: 1px solid rgba(255,255,255,0.06);
  background: rgba(255,255,255,0.02);
}
.ai-chat-input {
  flex: 1;
  padding: 10px 14px;
  border-radius: 10px;
  border: 1px solid rgba(255,255,255,0.1);
  background: rgba(255,255,255,0.04);
  color: #e2e8f0;
  font-size: 14px;
}
.ai-chat-input:focus { outline: none; border-color: rgba(99,102,241,0.4); }
.ai-chat-input::placeholder { color: #475569; }
.ai-chat-send {
  padding: 10px 18px;
  border-radius: 10px;
  background: linear-gradient(135deg, #ffca28, #2962ff);
  color: #111827;
  font-weight: 700;
  font-size: 14px;
  border: none;
  cursor: pointer;
  transition: opacity 0.2s;
  white-space: nowrap;
}
.ai-chat-send:hover { opacity: 0.85; }
.ai-chat-send:disabled { opacity: 0.4; cursor: not-allowed; }

@media (max-width: 960px) {
  .hero-panel {
    grid-template-columns: 1fr;
  }

  .overview-grid {
    grid-template-columns: 1fr;
  }

  .home-header {
    flex-direction: column;
    align-items: flex-start;
  }

  .ai-chat-panel {
    width: calc(100vw - 24px);
    right: 12px;
    bottom: 84px;
    height: 60vh;
  }
}
</style>
