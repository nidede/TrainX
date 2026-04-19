<template>
  <div class="problem-detail-page">
    <header class="pd-header">
      <div class="pd-header-inner">
        <button class="pd-back" @click="goBack">← 返回知识库</button>
        <span v-if="problem" class="pd-header-info">
          <span class="pd-title">{{ problem.title }}</span>
          <span class="pd-diff">Lv{{ problem.unified_difficulty || '—' }}</span>
          <a v-if="problem.source_url" :href="problem.source_url" target="_blank" rel="noopener" class="pd-source">原题链接 ↗</a>
        </span>
      </div>
    </header>

    <div v-if="loading" class="pd-loading">加载中…</div>

    <div v-else-if="problem" class="pd-body">
      <!-- 左侧：题目描述 -->
      <div class="pd-left">
        <div class="pd-desc-area">
          <div v-if="problem.tags && problem.tags.length" class="pd-tags">
            <span v-for="t in problem.tags" :key="t.id" class="pd-tag">{{ t.name }}</span>
          </div>
          <div v-if="descLoading" class="pd-desc-loading">
            <div class="pd-loading-spinner"></div>
            <span>正在从原题翻译…</span>
          </div>
          <div v-else-if="translatedDesc" class="pd-desc-content" v-html="renderedDesc"></div>
          <div v-else class="pd-desc-empty">
            <div class="pd-empty-icon">📝</div>
            <p>题目描述暂未录入</p>
            <p class="pd-empty-hint">你可以点击上方「原题链接」查看原题，或在右侧向 AI 助手提问</p>
          </div>
        </div>
      </div>

      <!-- 右侧：AI 对话 -->
      <div class="pd-right">
        <div class="pd-chat">
          <div class="pd-chat-header">
            <span>AI 解题助手</span>
          </div>
          <div class="pd-chat-messages" ref="chatMessagesRef">
            <div v-if="chatMessages.length === 0" class="pd-chat-welcome">
              <p>你好！我是 AI 解题助手。</p>
              <p>你可以向我提问关于这道题的思路、算法或优化方案。</p>
            </div>
            <div v-for="(msg, i) in chatMessages" :key="i" :class="['pd-chat-msg', `pd-chat-msg--${msg.role}`]">
              <div class="pd-chat-msg-text">{{ msg.content }}</div>
            </div>
            <div v-if="chatLoading" class="pd-chat-msg pd-chat-msg--assistant">
              <div class="pd-chat-msg-text pd-typing">思考中…</div>
            </div>
          </div>
          <div class="pd-chat-input-bar">
            <input
              v-model="chatInput"
              placeholder="向 AI 提问…"
              class="pd-chat-input"
              @keydown.enter="sendMessage"
              :disabled="chatLoading"
            />
            <button class="pd-chat-send" :disabled="!chatInput.trim() || chatLoading" @click="sendMessage">发送</button>
          </div>
        </div>
      </div>
    </div>

    <div v-else class="pd-loading">题目不存在</div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import axios from 'axios'
import 'katex/dist/katex.min.css'

const route = useRoute()
const router = useRouter()
const problemId = route.params.id

const problem = ref(null)
const loading = ref(false)
const translatedDesc = ref('')
const descLoading = ref(false)

// ── AI 聊天 ──
const chatInput = ref('')
const chatLoading = ref(false)
const chatMessages = ref([])
const chatMessagesRef = ref(null)
const conversationId = ref('')

async function fetchProblem() {
  loading.value = true
  try {
    const res = await axios.get(`/api/problems/${problemId}/`)
    problem.value = res.data

    // 优先显示翻译后的描述，其次原始描述
    const td = problem.value.translated_description || ''
    const od = problem.value.description || ''
    if (td) {
      translatedDesc.value = td
    } else if (od && od.trim() !== '' && od.trim() !== '题目描述请访问原题链接。') {
      translatedDesc.value = od
    } else if (problem.value.source_url) {
      // 没有任何描述但有原题链接，自动翻译
      translateProblem()
    }
  } catch (e) {
    console.error('获取题目失败', e)
  } finally {
    loading.value = false
  }
}

async function translateProblem() {
  descLoading.value = true
  try {
    const res = await axios.get(`/api/problems/${problemId}/translate/`)
    if (res.data.description) {
      translatedDesc.value = res.data.description
    }
  } catch (e) {
    console.error('翻译失败', e)
  } finally {
    descLoading.value = false
  }
}

const renderedDesc = computed(() => {
  if (!translatedDesc.value) return ''
  return window.renderMarkdown(translatedDesc.value)
})

async function sendMessage() {
  const text = chatInput.value.trim()
  if (!text || chatLoading.value) return
  chatMessages.value.push({ role: 'user', content: text })
  chatInput.value = ''
  chatLoading.value = true
  await nextTick()
  scrollToBottom()

  // 把题目信息附加到消息中（首次对话时）
  let message = text
  if (chatMessages.value.length <= 2 && problem.value) {
    message = `[当前题目：${problem.value.title}，难度 Lv${problem.value.unified_difficulty || '?'}，知识点：${(problem.value.tags || []).map(t => t.name).join('、') || '无'}]\n\n${text}`
  }

  try {
    const res = await axios.post('/api/users/coze-chat/', {
      message,
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

function goBack() {
  router.push('/problems')
}

onMounted(fetchProblem)
</script>

<style scoped>
.problem-detail-page {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  color: #e6eef8;
  background: #0b1120;
}

/* ── 顶栏 ── */
.pd-header {
  background: rgba(255,255,255,0.02);
  border-bottom: 1px solid rgba(255,255,255,0.06);
  padding: 12px 0;
  flex-shrink: 0;
}
.pd-header-inner {
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 24px;
  display: flex;
  align-items: center;
  gap: 20px;
}
.pd-back {
  padding: 7px 14px;
  border-radius: 8px;
  background: rgba(255,255,255,0.1);
  border: 1px solid rgba(255,255,255,0.2);
  color: #fff;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
  white-space: nowrap;
}
.pd-back:hover { background: rgba(255,255,255,0.15); }
.pd-header-info {
  display: flex;
  align-items: center;
  gap: 12px;
  min-width: 0;
}
.pd-title {
  font-size: 16px;
  font-weight: 700;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.pd-diff {
  font-size: 12px;
  font-weight: 600;
  padding: 2px 10px;
  border-radius: 12px;
  background: rgba(99,102,241,0.15);
  color: #c7d2fe;
  flex-shrink: 0;
}
.pd-source {
  font-size: 12px;
  color: #818cf8;
  text-decoration: none;
  white-space: nowrap;
  flex-shrink: 0;
}
.pd-source:hover { text-decoration: underline; }

/* ── 主体 ── */
.pd-body {
  flex: 1;
  display: flex;
  min-height: 0;
  overflow: hidden;
}

/* ── 左侧：题目描述 ── */
.pd-left {
  flex: 1;
  display: flex;
  flex-direction: column;
  border-right: 1px solid rgba(255,255,255,0.06);
  overflow-y: auto;
}
.pd-desc-area {
  padding: 28px 32px;
  max-width: 100%;
}
.pd-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 20px;
}
.pd-tag {
  display: inline-block;
  background: rgba(99,102,241,0.12);
  color: #c7d2fe;
  padding: 5px 12px;
  border-radius: 16px;
  font-size: 12px;
}
.pd-desc-content {
  font-size: 15px;
  line-height: 1.8;
  color: #cbd5e1;
}
.pd-desc-content :deep(h1) { font-size: 22px; font-weight: 800; color: #fff; margin: 28px 0 14px; padding-bottom: 8px; border-bottom: 1px solid rgba(255,255,255,0.08); }
.pd-desc-content :deep(h2) { font-size: 19px; font-weight: 700; color: #fff; margin: 24px 0 12px; padding-bottom: 6px; border-bottom: 1px solid rgba(255,255,255,0.06); }
.pd-desc-content :deep(h3) { font-size: 16px; font-weight: 700; color: #e2e8f0; margin: 18px 0 8px; }
.pd-desc-content :deep(h4) { font-size: 15px; font-weight: 700; color: #e2e8f0; margin: 14px 0 6px; }
.pd-desc-content :deep(p) { margin: 0 0 12px; }
.pd-desc-content :deep(blockquote) {
  margin: 14px 0; padding: 10px 18px;
  border-left: 3px solid #818cf8; background: rgba(99,102,241,0.06);
  color: #94a3b8; border-radius: 0 8px 8px 0;
}
.pd-desc-content :deep(code) {
  font-family: 'Fira Code', 'Consolas', 'Courier New', monospace;
  background: rgba(255,255,255,0.08); padding: 2px 7px;
  border-radius: 4px; font-size: 13px; color: #fbbf24;
}
.pd-desc-content :deep(pre) {
  background: #0d1117; border: 1px solid rgba(255,255,255,0.08);
  border-radius: 10px; padding: 16px 20px; overflow-x: auto; margin: 14px 0;
  line-height: 1.5;
}
.pd-desc-content :deep(pre code) { background: none; padding: 0; color: #e2e8f0; font-size: 13px; }
.pd-desc-content :deep(ul) { padding-left: 22px; margin: 8px 0; }
.pd-desc-content :deep(ol) { padding-left: 22px; margin: 8px 0; }
.pd-desc-content :deep(li) { margin-bottom: 6px; }
.pd-desc-content :deep(li)::marker { color: #64748b; }
.pd-desc-content :deep(strong) { color: #fff; font-weight: 700; }
.pd-desc-content :deep(em) { color: #fbbf24; font-style: italic; }
.pd-desc-content :deep(a) { color: #818cf8; text-decoration: underline; }
.pd-desc-content :deep(hr) { border: none; border-top: 1px solid rgba(255,255,255,0.08); margin: 20px 0; }
.pd-desc-content :deep(table) {
  width: 100%; border-collapse: collapse; margin: 14px 0;
  font-size: 14px;
}
.pd-desc-content :deep(th) {
  background: rgba(255,255,255,0.06); color: #e2e8f0;
  padding: 8px 12px; text-align: left; font-weight: 600;
  border: 1px solid rgba(255,255,255,0.08);
}
.pd-desc-content :deep(td) {
  padding: 8px 12px;
  border: 1px solid rgba(255,255,255,0.06);
}
.pd-desc-content :deep(tr:nth-child(even)) { background: rgba(255,255,255,0.02); }
.pd-desc-content :deep(img) { max-width: 100%; border-radius: 8px; margin: 8px 0; }
.pd-desc-content :deep(.math-inline), .pd-desc-content :deep(.math) {
  font-family: 'Times New Roman', serif; font-style: italic; color: #c7d2fe;
}
.pd-desc-empty {
  text-align: center;
  padding: 80px 20px;
  color: #64748b;
}
.pd-empty-icon {
  font-size: 48px;
  margin-bottom: 16px;
}
.pd-empty-hint {
  font-size: 13px;
  margin-top: 8px;
  color: #475569;
}
.pd-desc-loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 14px;
  padding: 80px 20px;
  color: #64748b;
  font-size: 14px;
}
.pd-loading-spinner {
  width: 32px;
  height: 32px;
  border: 3px solid rgba(255,255,255,0.1);
  border-top-color: #818cf8;
  border-radius: 50%;
  animation: pd-spin 0.8s linear infinite;
}
@keyframes pd-spin {
  to { transform: rotate(360deg); }
}

/* ── 右侧：AI 对话 ── */
.pd-right {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-width: 0;
}
.pd-chat {
  display: flex;
  flex-direction: column;
  height: 100%;
}
.pd-chat-header {
  padding: 12px 18px;
  background: rgba(255,255,255,0.03);
  border-bottom: 1px solid rgba(255,255,255,0.06);
  font-weight: 700;
  font-size: 14px;
  color: #e2e8f0;
  flex-shrink: 0;
}
.pd-chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 10px;
}
.pd-chat-welcome {
  text-align: center;
  color: #64748b;
  font-size: 13px;
  padding: 30px 10px;
  line-height: 1.8;
}
.pd-chat-msg {
  max-width: 88%;
}
.pd-chat-msg--user { align-self: flex-end; }
.pd-chat-msg--assistant { align-self: flex-start; }
.pd-chat-msg-text {
  padding: 10px 14px;
  border-radius: 12px;
  font-size: 14px;
  line-height: 1.6;
  white-space: pre-wrap;
  word-break: break-word;
}
.pd-chat-msg--user .pd-chat-msg-text {
  background: linear-gradient(135deg, #2962ff, #1e40af);
  color: #fff;
  border-bottom-right-radius: 4px;
}
.pd-chat-msg--assistant .pd-chat-msg-text {
  background: rgba(255,255,255,0.06);
  color: #e2e8f0;
  border-bottom-left-radius: 4px;
}
.pd-typing { color: #64748b; font-style: italic; }
.pd-chat-input-bar {
  display: flex;
  gap: 8px;
  padding: 12px 16px;
  border-top: 1px solid rgba(255,255,255,0.06);
  background: rgba(255,255,255,0.02);
  flex-shrink: 0;
}
.pd-chat-input {
  flex: 1;
  padding: 10px 14px;
  border-radius: 10px;
  border: 1px solid rgba(255,255,255,0.1);
  background: rgba(255,255,255,0.04);
  color: #e2e8f0;
  font-size: 14px;
}
.pd-chat-input:focus { outline: none; border-color: rgba(99,102,241,0.4); }
.pd-chat-input::placeholder { color: #475569; }
.pd-chat-send {
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
.pd-chat-send:hover { opacity: 0.85; }
.pd-chat-send:disabled { opacity: 0.4; cursor: not-allowed; }

.pd-loading {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #64748b;
}

@media (max-width: 720px) {
  .pd-body { flex-direction: column; }
  .pd-left { border-right: none; border-bottom: 1px solid rgba(255,255,255,0.06); max-height: 40vh; }
  .pd-right { min-height: 50vh; }
  .pd-header-inner { padding: 0 16px; }
}
</style>
