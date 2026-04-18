<template>
  <div class="blog-page">
    <header class="blog-header">
      <div class="blog-header-inner">
        <div class="blog-header-left">
          <button class="back-btn" @click="goBack">返回</button>
          <h1>竞赛博客</h1>
        </div>
        <div class="blog-header-right">
          <input v-model="search" placeholder="搜索文章…" class="search-input" @input="onSearchInput" />
          <router-link v-if="isLoggedIn" to="/blog/create" class="write-btn">写文章</router-link>
        </div>
      </div>
    </header>

    <div class="blog-body">
      <div class="blog-sidebar">
        <div class="sidebar-section">
          <h3 class="sidebar-title">分类</h3>
          <button
            :class="['cat-btn', { active: !selectedCategory }]"
            @click="selectCategory(null)"
          >全部</button>
          <button
            v-for="cat in categories"
            :key="cat.id"
            :class="['cat-btn', { active: selectedCategory === cat.id }]"
            @click="selectCategory(cat.id)"
          >{{ cat.name }} <span class="cat-count">{{ cat.post_count }}</span></button>
        </div>
        <div v-if="isLoggedIn" class="sidebar-section">
          <button
            :class="['cat-btn', { active: showMyPosts }]"
            @click="showMyPosts = !showMyPosts; fetchPosts()"
          >我的文章</button>
        </div>
      </div>

      <div class="blog-main">
        <div v-if="loading" class="loading">加载中…</div>
        <div v-else-if="posts.length === 0" class="empty">暂无文章</div>
        <template v-else>
          <article v-for="post in posts" :key="post.id" class="post-card" @click="goToPost(post.id)">
            <div class="post-card-top">
              <span v-if="post.category_name" class="post-category">{{ post.category_name }}</span>
              <span v-if="!post.is_published" class="post-draft">草稿</span>
            </div>
            <h2 class="post-title">{{ post.title }}</h2>
            <p v-if="post.summary" class="post-summary">{{ post.summary }}</p>
            <div class="post-meta">
              <span class="post-author">{{ post.author }}</span>
              <span class="post-dot">·</span>
              <span class="post-date">{{ formatDate(post.created_at) }}</span>
              <span class="post-dot">·</span>
              <span class="post-views">{{ post.view_count }} 阅读</span>
              <span class="post-dot">·</span>
              <span class="post-comments">{{ post.comment_count }} 评论</span>
            </div>
          </article>
        </template>

        <nav v-if="totalPages > 1" class="pagination">
          <button class="page-btn" :disabled="currentPage <= 1" @click="goPage(1)">«</button>
          <button class="page-btn" :disabled="currentPage <= 1" @click="goPage(currentPage - 1)">‹</button>
          <template v-for="p in visiblePages" :key="p">
            <span v-if="p === '...'" class="page-ellipsis">…</span>
            <button v-else :class="['page-btn', { active: p === currentPage }]" @click="goPage(p)">{{ p }}</button>
          </template>
          <button class="page-btn" :disabled="currentPage >= totalPages" @click="goPage(currentPage + 1)">›</button>
          <button class="page-btn" :disabled="currentPage >= totalPages" @click="goPage(totalPages)">»</button>
        </nav>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'

const router = useRouter()

const posts = ref([])
const categories = ref([])
const loading = ref(false)
const search = ref('')
const selectedCategory = ref(null)
const showMyPosts = ref(false)
const currentPage = ref(1)
const totalCount = ref(0)
const pageSize = 10

const isLoggedIn = computed(() => !!localStorage.getItem('trainx_token'))
const totalPages = computed(() => Math.ceil(totalCount.value / pageSize))

const visiblePages = computed(() => {
  const total = totalPages.value
  const cur = currentPage.value
  if (total <= 5) return Array.from({ length: total }, (_, i) => i + 1)
  const pages = [1]
  if (cur > 3) pages.push('...')
  for (let i = Math.max(2, cur - 1); i <= Math.min(total - 1, cur + 1); i++) {
    pages.push(i)
  }
  if (cur < total - 2) pages.push('...')
  pages.push(total)
  return pages
})

let searchTimer = null
function onSearchInput() {
  clearTimeout(searchTimer)
  searchTimer = setTimeout(() => { currentPage.value = 1; fetchPosts() }, 300)
}

function selectCategory(id) {
  selectedCategory.value = id
  currentPage.value = 1
  fetchPosts()
}

async function fetchCategories() {
  try {
    const res = await axios.get('/api/blog/categories/')
    categories.value = res.data
  } catch (e) {
    console.error('获取分类失败', e)
  }
}

async function fetchPosts() {
  loading.value = true
  try {
    const params = new URLSearchParams({ page: currentPage.value })
    if (selectedCategory.value) params.set('category', selectedCategory.value)
    if (search.value.trim()) params.set('search', search.value.trim())
    if (showMyPosts.value) {
      const user = localStorage.getItem('trainx_user')
      if (user) params.set('author', user)
    }
    const res = await axios.get(`/api/blog/posts/?${params}`)
    posts.value = res.data.results || []
    totalCount.value = res.data.count || 0
  } catch (e) {
    console.error('获取文章失败', e)
  } finally {
    loading.value = false
  }
}

function goPage(page) {
  if (page < 1 || page > totalPages.value || page === currentPage.value) return
  currentPage.value = page
  fetchPosts()
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

function goToPost(id) {
  router.push(`/blog/${id}`)
}

function goBack() {
  router.push('/home')
}

function formatDate(dateStr) {
  if (!dateStr) return ''
  const d = new Date(dateStr)
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`
}

onMounted(() => {
  fetchCategories()
  fetchPosts()
})
</script>

<style scoped>
.blog-page {
  min-height: 100vh;
  color: #e6eef8;
  background: radial-gradient(ellipse at 20% 0%, rgba(255,202,40,0.06), transparent 50%),
              radial-gradient(ellipse at 80% 100%, rgba(41,98,255,0.06), transparent 50%),
              #0b1120;
}

/* ── 顶栏 ── */
.blog-header {
  background: rgba(255,255,255,0.02);
  border-bottom: 1px solid rgba(255,255,255,0.06);
  padding: 18px 0;
}
.blog-header-inner {
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 48px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 16px;
}
.blog-header-left {
  display: flex;
  align-items: center;
  gap: 16px;
}
.blog-header-left h1 {
  margin: 0;
  font-size: 28px;
  font-weight: 800;
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
.blog-header-right {
  display: flex;
  align-items: center;
  gap: 12px;
}
.search-input {
  padding: 9px 14px;
  border-radius: 10px;
  border: 1px solid rgba(255,255,255,0.1);
  background: rgba(255,255,255,0.04);
  color: #cbd5e1;
  min-width: 200px;
}
.search-input:focus { outline: none; border-color: rgba(99,102,241,0.4); }
.write-btn {
  padding: 9px 20px;
  border-radius: 10px;
  background: linear-gradient(135deg, #ffca28, #2962ff);
  color: #111827;
  font-weight: 700;
  font-size: 14px;
  text-decoration: none;
  transition: opacity 0.2s;
}
.write-btn:hover { opacity: 0.85; }

/* ── 主体布局 ── */
.blog-body {
  max-width: 1400px;
  margin: 0 auto;
  padding: 28px 48px;
  display: flex;
  gap: 32px;
}

/* ── 侧边栏 ── */
.blog-sidebar {
  width: 220px;
  flex-shrink: 0;
}
.sidebar-section {
  margin-bottom: 24px;
}
.sidebar-title {
  font-size: 13px;
  font-weight: 700;
  color: #64748b;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin: 0 0 10px;
}
.cat-btn {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
  padding: 8px 12px;
  margin-bottom: 4px;
  border-radius: 8px;
  border: none;
  background: transparent;
  color: #94a3b8;
  font-size: 14px;
  text-align: left;
  cursor: pointer;
  transition: all 0.15s ease;
}
.cat-btn:hover { background: rgba(255,255,255,0.05); color: #e2e8f0; }
.cat-btn.active { background: rgba(99,102,241,0.15); color: #c7d2fe; }
.cat-count {
  font-size: 11px;
  color: #64748b;
}

/* ── 文章列表 ── */
.blog-main {
  flex: 1;
  min-width: 0;
}
.post-card {
  padding: 20px 24px;
  margin-bottom: 12px;
  border-radius: 12px;
  background: rgba(255,255,255,0.02);
  border: 1px solid rgba(255,255,255,0.04);
  cursor: pointer;
  transition: all 0.2s ease;
}
.post-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 8px 24px rgba(0,0,0,0.4);
  border-color: rgba(255,255,255,0.1);
}
.post-card-top {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
}
.post-category {
  font-size: 11px;
  font-weight: 600;
  padding: 3px 10px;
  border-radius: 12px;
  background: rgba(99,102,241,0.15);
  color: #c7d2fe;
}
.post-draft {
  font-size: 11px;
  font-weight: 600;
  padding: 3px 10px;
  border-radius: 12px;
  background: rgba(251,191,36,0.15);
  color: #fbbf24;
}
.post-title {
  margin: 0 0 8px;
  font-size: 20px;
  font-weight: 700;
  color: #fff;
}
.post-summary {
  margin: 0 0 12px;
  color: #94a3b8;
  font-size: 14px;
  line-height: 1.6;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
.post-meta {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  color: #64748b;
}
.post-author { color: #94a3b8; font-weight: 600; }
.post-dot { opacity: 0.4; }

/* ── 分页 ── */
.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 6px;
  margin-top: 28px;
  padding: 16px 0;
}
.page-btn {
  min-width: 36px;
  height: 36px;
  border-radius: 8px;
  border: 1px solid rgba(255,255,255,0.12);
  background: rgba(255,255,255,0.04);
  color: #cbd5e1;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.15s ease;
}
.page-btn:hover:not(:disabled):not(.active) {
  background: rgba(255,255,255,0.1);
}
.page-btn.active {
  background: linear-gradient(135deg, #ffca28, #2962ff);
  border-color: transparent;
  color: #111827;
}
.page-btn:disabled { opacity: 0.3; cursor: not-allowed; }
.page-ellipsis { color: #64748b; font-size: 16px; padding: 0 4px; }

.loading, .empty {
  padding: 60px 0;
  text-align: center;
  color: #64748b;
  font-size: 15px;
}

@media (max-width: 720px) {
  .blog-body { flex-direction: column; padding: 20px; }
  .blog-sidebar { width: 100%; }
  .blog-header-inner { padding: 0 20px; flex-wrap: wrap; }
}
</style>
