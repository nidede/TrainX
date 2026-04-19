<template>
  <div class="detail-page">
    <header class="detail-header">
      <div class="detail-header-inner">
        <button class="back-btn" @click="goBack">← 返回博客</button>
      </div>
    </header>

    <div v-if="loading" class="loading">加载中…</div>

    <article v-else-if="post" class="detail-body">
      <div class="detail-top">
        <span v-if="post.category_name" class="detail-category">{{ post.category_name }}</span>
        <span v-if="!post.is_published" class="detail-draft">草稿</span>
      </div>
      <h1 class="detail-title">{{ post.title }}</h1>
      <div class="detail-meta">
        <span class="detail-author">{{ post.author }}</span>
        <span class="meta-dot">·</span>
        <span>{{ formatDate(post.created_at) }}</span>
        <span class="meta-dot">·</span>
        <span>{{ post.view_count }} 阅读</span>
        <span class="meta-dot">·</span>
        <span>{{ post.comments.length }} 评论</span>
        <template v-if="isAuthor">
          <span class="meta-dot">·</span>
          <router-link :to="`/blog/${post.id}/edit`" class="edit-link">编辑</router-link>
          <span class="meta-dot">·</span>
          <button class="delete-link" @click="deletePost">删除</button>
        </template>
      </div>

      <div class="detail-content" v-html="renderedContent"></div>

      <!-- 评论区 -->
      <section class="comments-section">
        <h2 class="comments-title">评论 ({{ post.comments.length }})</h2>

        <div v-if="isLoggedIn" class="comment-form">
          <textarea v-model="newComment" placeholder="写下你的评论…" rows="3" class="comment-input"></textarea>
          <button class="comment-submit" :disabled="!newComment.trim()" @click="submitComment">发表评论</button>
        </div>
        <div v-else class="comment-login-hint">
          <router-link to="/login">登录</router-link> 后可以评论
        </div>

        <div v-if="post.comments.length === 0" class="no-comments">暂无评论</div>
        <div v-for="c in post.comments" :key="c.id" class="comment-item">
          <div class="comment-avatar">{{ (c.author || '?')[0] }}</div>
          <div class="comment-body">
            <div class="comment-head">
              <span class="comment-author">{{ c.author }}</span>
              <span class="comment-date">{{ formatDate(c.created_at) }}</span>
              <button v-if="isCommentAuthor(c)" class="comment-delete" @click="deleteComment(c.id)">删除</button>
            </div>
            <p class="comment-text">{{ c.content }}</p>
          </div>
        </div>
      </section>
    </article>

    <div v-else class="empty">文章不存在</div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import axios from 'axios'

const route = useRoute()
const router = useRouter()
const postId = route.params.id

const post = ref(null)
const loading = ref(false)
const newComment = ref('')

const isLoggedIn = computed(() => !!localStorage.getItem('trainx_token'))
const isAuthor = computed(() => {
  if (!post.value || !isLoggedIn.value) return false
  const username = localStorage.getItem('trainx_user')
  return post.value.author === username
})

function isCommentAuthor(c) {
  if (!isLoggedIn.value) return false
  const username = localStorage.getItem('trainx_user')
  return c.author === username
}

const renderedContent = computed(() => {
  if (!post.value) return ''
  return window.renderMarkdown(post.value.content)
})

async function fetchPost() {
  loading.value = true
  try {
    const res = await axios.get(`/api/blog/posts/${postId}/`)
    post.value = res.data
  } catch (e) {
    console.error('获取文章失败', e)
  } finally {
    loading.value = false
  }
}

async function submitComment() {
  if (!newComment.value.trim()) return
  try {
    const res = await axios.post(`/api/blog/posts/${postId}/comments/`, {
      content: newComment.value.trim(),
    })
    post.value.comments.push(res.data)
    newComment.value = ''
  } catch (e) {
    console.error('发表评论失败', e)
  }
}

async function deleteComment(commentId) {
  try {
    await axios.delete(`/api/blog/posts/${postId}/comments/${commentId}/`)
    post.value.comments = post.value.comments.filter(c => c.id !== commentId)
  } catch (e) {
    console.error('删除评论失败', e)
  }
}

async function deletePost() {
  if (!confirm('确定要删除这篇文章吗？')) return
  try {
    await axios.delete(`/api/blog/posts/${postId}/`)
    router.push('/blog')
  } catch (e) {
    console.error('删除文章失败', e)
  }
}

function goBack() {
  router.push('/blog')
}

function formatDate(dateStr) {
  if (!dateStr) return ''
  const d = new Date(dateStr)
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`
}

onMounted(fetchPost)
</script>

<style scoped>
.detail-page {
  min-height: 100vh;
  color: #e6eef8;
  background: radial-gradient(ellipse at 20% 0%, rgba(255,202,40,0.06), transparent 50%),
              radial-gradient(ellipse at 80% 100%, rgba(41,98,255,0.06), transparent 50%),
              #0b1120;
}

/* ── 顶栏 ── */
.detail-header {
  background: rgba(255,255,255,0.02);
  border-bottom: 1px solid rgba(255,255,255,0.06);
  padding: 14px 0;
}
.detail-header-inner {
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 48px;
}
.back-btn {
  padding: 8px 16px;
  border-radius: 8px;
  background: rgba(255,255,255,0.1);
  border: 1px solid rgba(255,255,255,0.2);
  color: #fff;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
}
.back-btn:hover { background: rgba(255,255,255,0.15); }

/* ── 文章主体 ── */
.detail-body {
  max-width: 900px;
  margin: 0 auto;
  padding: 36px 48px 60px;
}
.detail-top {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
}
.detail-category {
  font-size: 11px;
  font-weight: 600;
  padding: 3px 10px;
  border-radius: 12px;
  background: rgba(99,102,241,0.15);
  color: #c7d2fe;
}
.detail-draft {
  font-size: 11px;
  font-weight: 600;
  padding: 3px 10px;
  border-radius: 12px;
  background: rgba(251,191,36,0.15);
  color: #fbbf24;
}
.detail-title {
  font-size: 32px;
  font-weight: 800;
  color: #fff;
  margin: 0 0 14px;
  line-height: 1.3;
}
.detail-meta {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  color: #64748b;
  margin-bottom: 32px;
  flex-wrap: wrap;
}
.detail-author { color: #94a3b8; font-weight: 600; }
.meta-dot { opacity: 0.4; }
.edit-link {
  color: #818cf8;
  text-decoration: none;
  font-weight: 600;
}
.edit-link:hover { text-decoration: underline; }
.delete-link {
  background: none;
  border: none;
  color: #f87171;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  padding: 0;
}
.delete-link:hover { text-decoration: underline; }

/* ── 文章内容 ── */
.detail-content {
  font-size: 16px;
  line-height: 1.8;
  color: #cbd5e1;
}
.detail-content :deep(h1) { font-size: 26px; font-weight: 800; color: #fff; margin: 36px 0 14px; border-bottom: 1px solid rgba(255,255,255,0.08); padding-bottom: 8px; }
.detail-content :deep(h2) { font-size: 22px; font-weight: 700; color: #fff; margin: 28px 0 12px; border-bottom: 1px solid rgba(255,255,255,0.06); padding-bottom: 6px; }
.detail-content :deep(h3) { font-size: 18px; font-weight: 700; color: #e2e8f0; margin: 22px 0 10px; }
.detail-content :deep(h4) { font-size: 16px; font-weight: 700; color: #e2e8f0; margin: 16px 0 8px; }
.detail-content :deep(p) { margin: 0 0 14px; }
.detail-content :deep(blockquote) {
  margin: 16px 0; padding: 10px 18px;
  border-left: 3px solid #818cf8; background: rgba(99,102,241,0.06);
  color: #94a3b8; border-radius: 0 8px 8px 0;
}
.detail-content :deep(code) {
  font-family: 'Fira Code', 'Consolas', 'Courier New', monospace;
  background: rgba(255,255,255,0.08); padding: 2px 7px;
  border-radius: 4px; font-size: 14px; color: #fbbf24;
}
.detail-content :deep(pre) {
  background: #0d1117; border: 1px solid rgba(255,255,255,0.08);
  border-radius: 10px; padding: 16px 20px; overflow-x: auto; margin: 16px 0;
  line-height: 1.5;
}
.detail-content :deep(pre code) { background: none; padding: 0; color: #e2e8f0; font-size: 13px; }
.detail-content :deep(ul) { padding-left: 22px; margin: 8px 0; }
.detail-content :deep(ol) { padding-left: 22px; margin: 8px 0; }
.detail-content :deep(li) { margin-bottom: 6px; }
.detail-content :deep(li)::marker { color: #64748b; }
.detail-content :deep(a) { color: #818cf8; text-decoration: underline; }
.detail-content :deep(strong) { color: #fff; font-weight: 700; }
.detail-content :deep(em) { color: #fbbf24; font-style: italic; }
.detail-content :deep(hr) { border: none; border-top: 1px solid rgba(255,255,255,0.08); margin: 24px 0; }
.detail-content :deep(table) { width: 100%; border-collapse: collapse; margin: 14px 0; font-size: 14px; }
.detail-content :deep(th) { background: rgba(255,255,255,0.06); color: #e2e8f0; padding: 8px 12px; text-align: left; font-weight: 600; border: 1px solid rgba(255,255,255,0.08); }
.detail-content :deep(td) { padding: 8px 12px; border: 1px solid rgba(255,255,255,0.06); }
.detail-content :deep(tr:nth-child(even)) { background: rgba(255,255,255,0.02); }
.detail-content :deep(img) { max-width: 100%; border-radius: 8px; margin: 8px 0; }

/* ── 评论区 ── */
.comments-section {
  margin-top: 48px;
  border-top: 1px solid rgba(255,255,255,0.06);
  padding-top: 32px;
}
.comments-title {
  font-size: 18px;
  font-weight: 700;
  margin: 0 0 20px;
}
.comment-form {
  margin-bottom: 24px;
}
.comment-input {
  width: 100%;
  padding: 12px 16px;
  border-radius: 10px;
  border: 1px solid rgba(255,255,255,0.1);
  background: rgba(255,255,255,0.04);
  color: #e2e8f0;
  font-size: 14px;
  resize: vertical;
  font-family: inherit;
}
.comment-input:focus { outline: none; border-color: rgba(99,102,241,0.4); }
.comment-submit {
  margin-top: 10px;
  padding: 8px 20px;
  border-radius: 8px;
  background: linear-gradient(135deg, #ffca28, #2962ff);
  color: #111827;
  font-weight: 700;
  font-size: 14px;
  border: none;
  cursor: pointer;
  transition: opacity 0.2s;
}
.comment-submit:hover { opacity: 0.85; }
.comment-submit:disabled { opacity: 0.4; cursor: not-allowed; }
.comment-login-hint {
  padding: 14px;
  background: rgba(255,255,255,0.02);
  border-radius: 10px;
  color: #64748b;
  margin-bottom: 24px;
}
.comment-login-hint a { color: #818cf8; font-weight: 600; }
.no-comments { color: #64748b; font-size: 14px; }

.comment-item {
  display: flex;
  gap: 12px;
  padding: 14px 0;
  border-bottom: 1px solid rgba(255,255,255,0.04);
}
.comment-avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: rgba(99,102,241,0.2);
  color: #c7d2fe;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 14px;
  flex-shrink: 0;
}
.comment-body { flex: 1; min-width: 0; }
.comment-head {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 4px;
}
.comment-author { font-weight: 600; font-size: 14px; color: #e2e8f0; }
.comment-date { font-size: 12px; color: #64748b; }
.comment-delete {
  background: none;
  border: none;
  color: #f87171;
  font-size: 12px;
  cursor: pointer;
  margin-left: auto;
  opacity: 0.6;
}
.comment-delete:hover { opacity: 1; }
.comment-text {
  margin: 0;
  color: #cbd5e1;
  font-size: 14px;
  line-height: 1.6;
}

.loading, .empty {
  padding: 80px 0;
  text-align: center;
  color: #64748b;
}

@media (max-width: 720px) {
  .detail-body { padding: 20px; }
  .detail-title { font-size: 24px; }
}
</style>
