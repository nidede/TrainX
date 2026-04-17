<template>
  <div class="problems-page">
    <header class="page-header">
      <div class="header-left">
        <button class="back-button" @click="goBack">返回</button>
        <h1>结构化知识库</h1>
      </div>
    </header>

    <div class="toolbar">
      <input v-model="q" placeholder="按题名搜索" class="search-input" @input="onSearchInput" />

      <div class="tag-selector" ref="tagDropdownRef">
        <button class="tag-trigger" @click="tagDropdownOpen = !tagDropdownOpen">
          <span v-if="selectedTags.length === 0">选择知识点</span>
          <span v-else class="tag-trigger-selected">已选 {{ selectedTags.length }} 个知识点</span>
          <span class="tag-trigger-arrow">&#9662;</span>
        </button>
        <div v-if="tagDropdownOpen" class="tag-dropdown">
          <input v-model="tagSearch" placeholder="搜索知识点…" class="tag-search" />
          <div class="tag-list">
            <button
              v-for="tag in filteredTags"
              :key="tag"
              :class="['tag-option', { selected: selectedTagNames.includes(tag) }]"
              @click="toggleTag(tag)"
            >
              <span class="tag-check">{{ selectedTagNames.includes(tag) ? '✓' : '' }}</span>
              {{ tag }}
            </button>
          </div>
        </div>
      </div>

      <div class="difficulty-chips">
        <button
          v-for="d in difficultyOptions"
          :key="d.value"
          :class="['chip', { active: selectedDifficulties.includes(d.value) }]"
          @click="toggleDifficulty(d.value)"
        >{{ d.label }}</button>
      </div>
    </div>

    <div v-if="selectedTags.length > 0" class="selected-tags-bar">
      <span class="selected-label">已选知识点：</span>
      <span v-for="name in selectedTags" :key="name" class="selected-tag" @click="toggleTag(name)">
        {{ name }} ×
      </span>
      <button class="clear-tags" @click="clearTags">清除全部</button>
    </div>

    <div v-if="loading" class="loading">加载中…</div>

    <div v-else>
      <div v-if="filtered.length === 0" class="empty">没有符合条件的题目。</div>

      <section class="grid">
        <article v-for="p in filtered" :key="p.id" :class="['card', getCardClass(p.id)]">
          <div class="card-header">
            <a :href="p.source_url" target="_blank" rel="noopener noreferrer" class="card-title" @click="markAsAttempted(p.id)">{{ p.title }}</a>
            <div class="status-checkbox">
              <input type="checkbox" :id="`problem-${p.id}`" :checked="isSolved(p.id)" @change="toggleStatus(p.id)" />
              <label :for="`problem-${p.id}`"></label>
            </div>
          </div>
          <div class="meta">
            <span class="contest">{{ p.contest_name }}</span>
            <span class="dot">·</span>
            <span class="difficulty">Lv{{ p.unified_difficulty || '—' }}</span>
            <span class="dot">·</span>
            <span :class="['status', getStatusClass(p.id)]">{{ getStatusText(p.id) }}</span>
          </div>
          <div class="tags">
            <span v-for="t in p.tags" :key="t.id" class="tag">{{ t.name }}</span>
          </div>
        </article>
      </section>

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
</template>

<script setup>
import { ref, onMounted, computed, onBeforeUnmount } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'

const router = useRouter()

const problems = ref([])
const loading = ref(false)
const q = ref('')
const selectedDifficulties = ref([])
const selectedTags = ref([])
const tagSearch = ref('')
const tagDropdownOpen = ref(false)
const tagDropdownRef = ref(null)
const problemStatus = ref({})
const currentPage = ref(1)
const totalCount = ref(0)
const totalPages = ref(1)

const difficultyOptions = [
  { value: 0, label: 'Lv0 入门' },
  { value: 1, label: 'Lv1 简单' },
  { value: 2, label: 'Lv2 较易' },
  { value: 3, label: 'Lv3 中等' },
  { value: 4, label: 'Lv4 较难' },
  { value: 5, label: 'Lv5 困难' },
  { value: 6, label: 'Lv6 极难' },
]

const knowledgePoints = [
  '表达式解析', '调度', '三分查找', '网络流', '矩阵', '字符串后缀结构',
  '双指针', '并查集', '图匹配', '字符串', '最短路', '特殊问题', '哈希',
  '通信', '计算几何', '中国剩余定理', '图论', '组合数学', '博弈论',
  '状态压缩', '数论', '暴力', '交互题', '分治', '二分', '树', '概率',
  '快速傅里叶变换', '动态规划', '深度优先搜索', '模拟', '数据结构',
  '数学', '构造算法', '排序', '贪心', '折半搜索', '2-SAT',
]

function toggleDifficulty(val) {
  const idx = selectedDifficulties.value.indexOf(val)
  if (idx >= 0) {
    selectedDifficulties.value.splice(idx, 1)
  } else {
    selectedDifficulties.value.push(val)
  }
  fetchProblems(1)
}

let searchTimer = null
function onSearchInput() {
  clearTimeout(searchTimer)
  searchTimer = setTimeout(() => {
    fetchProblems(1)
  }, 350)
}

const selectedTagNames = computed(() => selectedTags.value)
const filteredTags = computed(() => {
  const s = tagSearch.value.trim().toLowerCase()
  if (!s) return knowledgePoints
  return knowledgePoints.filter(t => t.toLowerCase().includes(s))
})

function toggleTag(name) {
  const idx = selectedTags.value.indexOf(name)
  if (idx >= 0) {
    selectedTags.value.splice(idx, 1)
  } else {
    selectedTags.value.push(name)
  }
  fetchProblems(1)
}

function clearTags() {
  selectedTags.value = []
  fetchProblems(1)
}

// 点击外部关闭下拉
function onClickOutside(e) {
  if (tagDropdownRef.value && !tagDropdownRef.value.contains(e.target)) {
    tagDropdownOpen.value = false
  }
}
onMounted(() => document.addEventListener('click', onClickOutside))
onBeforeUnmount(() => document.removeEventListener('click', onClickOutside))

function goBack() {
  router.push('/home')
}

// 计算分页按钮中可见的页码（带省略号）
const visiblePages = computed(() => {
  const total = totalPages.value
  const cur = currentPage.value
  if (total <= 7) {
    return Array.from({ length: total }, (_, i) => i + 1)
  }
  const pages = []
  pages.push(1)
  if (cur > 3) pages.push('...')
  for (let i = Math.max(2, cur - 1); i <= Math.min(total - 1, cur + 1); i++) {
    pages.push(i)
  }
  if (cur < total - 2) pages.push('...')
  pages.push(total)
  return pages
})

// 获取题目列表（带分页）
async function fetchProblems(page = 1) {
  loading.value = true
  try {
    const params = new URLSearchParams({ page })
    if (selectedDifficulties.value.length > 0) {
      params.set('difficulty', selectedDifficulties.value.join(','))
    }
    if (selectedTags.value.length > 0) {
      params.set('tags', selectedTags.value.join(','))
    }
    const search = q.value.trim()
    if (search) {
      params.set('search', search)
    }
    const res = await axios.get(`/api/problems/?${params}`)
    problems.value = res.data.results || []
    totalCount.value = res.data.count || 0
    totalPages.value = Math.ceil(totalCount.value / 50)
    currentPage.value = page
  } catch (e) {
    console.error('获取题目列表失败', e)
  } finally {
    loading.value = false
  }
}

function goPage(page) {
  if (page < 1 || page > totalPages.value || page === currentPage.value) return
  fetchProblems(page)
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

onMounted(async () => {
  await fetchProblems(1)
  await fetchUserProblems()
})

// 获取用户做题记录
async function fetchUserProblems() {
  try {
    const res = await axios.get('/api/users/problems/')
    const userProblems = res.data.results || res.data || []
    userProblems.forEach(up => {
      problemStatus.value[up.problem.id] = {
        solved: up.solved,
        attempted: true
      }
    })
  } catch (e) {
    console.error('获取用户做题记录失败', e)
  }
}

// 标记题目为已尝试
async function markAsAttempted(problemId) {
  if (!problemStatus.value[problemId]) {
    problemStatus.value[problemId] = { solved: false, attempted: true }
    try {
      await axios.post('/api/users/problems/', { problem_id: problemId, solved: false })
    } catch (e) {
      console.error('保存题目状态失败', e)
    }
  }
}

// 切换题目的状态
async function toggleStatus(problemId) {
  const currentStatus = problemStatus.value[problemId] || { solved: false, attempted: false }
  const newSolved = !currentStatus.solved
  problemStatus.value[problemId] = { solved: newSolved, attempted: true }
  try {
    await axios.post('/api/users/problems/', { problem_id: problemId, solved: newSolved })
  } catch (e) {
    console.error('保存题目状态失败', e)
  }
}

function isSolved(problemId) {
  return problemStatus.value[problemId]?.solved || false
}

function getStatusText(problemId) {
  const status = problemStatus.value[problemId]
  if (!status) return '未做'
  if (status.solved) return '已完成'
  return '尝试中'
}

function getStatusClass(problemId) {
  const status = problemStatus.value[problemId]
  if (!status) return 'status-none'
  if (status.solved) return 'status-solved'
  return 'status-attempted'
}

function getCardClass(problemId) {
  const status = problemStatus.value[problemId]
  if (!status) return ''
  if (status.solved) return 'card-solved'
  if (status.attempted) return 'card-attempted'
  return ''
}

const filtered = computed(() => problems.value)
</script>

<style scoped>
.problems-page {
  padding: 28px 20px;
  max-width: 1100px;
  margin: 0 auto;
  color: #e6eef8;
}
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 16px;
  margin-bottom: 18px;
}
.header-left {
  display: flex;
  align-items: center;
  gap: 16px;
}
.back-button {
  padding: 8px 16px;
  border-radius: 8px;
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  color: #ffffff;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
}
.back-button:hover {
  background: rgba(255, 255, 255, 0.15);
  border-color: rgba(255, 255, 255, 0.3);
}
.page-header h1 {
  margin: 0;
  font-size: 36px;
  font-weight: 800;
}
.toolbar {
  display: flex;
  gap: 12px;
  align-items: center;
  flex-wrap: wrap;
  margin-bottom: 20px;
}
.search-input {
  padding: 10px 14px;
  border-radius: 10px;
  border: 1px solid rgba(255,255,255,0.1);
  background: rgba(255,255,255,0.04);
  color: #cbd5e1;
  min-width: 220px;
  flex-shrink: 0;
}
.search-input:focus {
  outline: none;
  border-color: rgba(99,102,241,0.4);
}
.difficulty-chips {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}
.chip {
  padding: 6px 12px;
  border-radius: 16px;
  border: 1px solid rgba(255,255,255,0.15);
  background: rgba(255,255,255,0.04);
  color: #94a3b8;
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.15s ease;
  white-space: nowrap;
}
.chip:hover {
  background: rgba(255,255,255,0.08);
  border-color: rgba(255,255,255,0.25);
}
.chip.active {
  background: rgba(99,102,241,0.2);
  border-color: rgba(99,102,241,0.5);
  color: #c7d2fe;
}

.tag-selector {
  position: relative;
}
.tag-trigger {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 9px 14px;
  border-radius: 10px;
  border: 1px solid rgba(255,255,255,0.12);
  background: rgba(255,255,255,0.04);
  color: #94a3b8;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.15s ease;
  white-space: nowrap;
}
.tag-trigger:hover {
  background: rgba(255,255,255,0.08);
  border-color: rgba(255,255,255,0.2);
}
.tag-trigger-selected {
  color: #c7d2fe;
  font-weight: 600;
}
.tag-trigger-arrow {
  font-size: 10px;
  opacity: 0.6;
}
.tag-dropdown {
  position: absolute;
  top: calc(100% + 6px);
  left: 0;
  width: 260px;
  max-height: 320px;
  background: #1a1f2e;
  border: 1px solid rgba(255,255,255,0.12);
  border-radius: 12px;
  box-shadow: 0 16px 48px rgba(0,0,0,0.5);
  z-index: 100;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}
.tag-search {
  margin: 10px;
  padding: 8px 10px;
  border-radius: 8px;
  border: 1px solid rgba(255,255,255,0.1);
  background: rgba(255,255,255,0.05);
  color: #cbd5e1;
  font-size: 13px;
  flex-shrink: 0;
}
.tag-search:focus {
  outline: none;
  border-color: rgba(99,102,241,0.4);
}
.tag-list {
  overflow-y: auto;
  padding: 4px 6px 10px;
  flex: 1;
}
.tag-option {
  display: flex;
  align-items: center;
  gap: 8px;
  width: 100%;
  padding: 7px 10px;
  border: none;
  border-radius: 6px;
  background: transparent;
  color: #cbd5e1;
  font-size: 13px;
  text-align: left;
  cursor: pointer;
  transition: background 0.1s;
}
.tag-option:hover {
  background: rgba(255,255,255,0.06);
}
.tag-option.selected {
  background: rgba(99,102,241,0.15);
  color: #c7d2fe;
}
.tag-check {
  width: 16px;
  text-align: center;
  font-size: 12px;
  color: #818cf8;
}

.selected-tags-bar {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 8px;
  margin-bottom: 16px;
}
.selected-label {
  color: #64748b;
  font-size: 13px;
  flex-shrink: 0;
}
.selected-tag {
  display: inline-flex;
  align-items: center;
  padding: 4px 10px;
  border-radius: 14px;
  background: rgba(99,102,241,0.18);
  border: 1px solid rgba(99,102,241,0.35);
  color: #c7d2fe;
  font-size: 12px;
  cursor: pointer;
  transition: all 0.15s ease;
}
.selected-tag:hover {
  background: rgba(99,102,241,0.28);
}
.clear-tags {
  padding: 4px 10px;
  border-radius: 14px;
  border: 1px solid rgba(255,82,82,0.3);
  background: rgba(255,82,82,0.08);
  color: #fca5a5;
  font-size: 12px;
  cursor: pointer;
  transition: all 0.15s ease;
}
.clear-tags:hover {
  background: rgba(255,82,82,0.16);
}
.loading { padding: 40px; color: #94a3b8 }
.empty { padding: 40px; color: #94a3b8 }
.grid {
  margin-top: 22px;
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 16px;
}
.card {
  padding: 18px;
  border-radius: 12px;
  background: linear-gradient(180deg, rgba(255,255,255,0.02), rgba(255,255,255,0.01));
  border: 1px solid rgba(255,255,255,0.04);
  transition: transform 150ms ease, box-shadow 150ms ease;
}
.card:hover { transform: translateY(-6px); box-shadow: 0 12px 30px rgba(0,0,0,0.6); }
.card-solved {
  border-color: rgba(74, 222, 128, 0.5);
  background: linear-gradient(180deg, rgba(74, 222, 128, 0.1), rgba(74, 222, 128, 0.05));
}
.card-attempted {
  border-color: rgba(251, 191, 36, 0.5);
  background: linear-gradient(180deg, rgba(251, 191, 36, 0.1), rgba(251, 191, 36, 0.05));
}
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 8px;
}
.card-title {
  font-size: 18px;
  font-weight: 700;
  color: #ffffff;
  text-decoration: none;
  flex: 1;
  margin-right: 12px;
}
.status-checkbox {
  position: relative;
  display: inline-block;
  width: 20px;
  height: 20px;
}
.status-checkbox input {
  position: absolute;
  opacity: 0;
  cursor: pointer;
  height: 0;
  width: 0;
}
.status-checkbox label {
  position: absolute;
  top: 0;
  left: 0;
  height: 20px;
  width: 20px;
  background-color: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.3);
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.2s ease;
}
.status-checkbox:hover label {
  background-color: rgba(255, 255, 255, 0.2);
}
.status-checkbox input:checked + label {
  background-color: #4ade80;
  border-color: #4ade80;
}
.status-checkbox input:checked + label:after {
  content: "";
  position: absolute;
  display: block;
  left: 6px;
  top: 2px;
  width: 6px;
  height: 12px;
  border: solid white;
  border-width: 0 2px 2px 0;
  transform: rotate(45deg);
}
.meta { color: #94a3b8; font-size: 13px; margin-top: 8px }
.status {
  font-weight: 600;
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 12px;
}
.status-none {
  color: #94a3b8;
  background: rgba(148, 163, 184, 0.1);
}
.status-solved {
  color: #4ade80;
  background: rgba(74, 222, 128, 0.1);
}
.status-attempted {
  color: #fbbf24;
  background: rgba(251, 191, 36, 0.1);
}
.tags { margin-top: 12px }
.tag {
  display: inline-block;
  margin-right: 8px;
  margin-bottom: 6px;
  background: rgba(99,102,241,0.12);
  color: #c7d2fe;
  padding: 6px 10px;
  border-radius: 16px;
  font-size: 12px;
}

.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 6px;
  margin-top: 32px;
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
  border-color: rgba(255,255,255,0.25);
}
.page-btn.active {
  background: linear-gradient(135deg, #ffca28, #2962ff);
  border-color: transparent;
  color: #111827;
}
.page-btn:disabled {
  opacity: 0.3;
  cursor: not-allowed;
}
.page-ellipsis {
  color: #64748b;
  font-size: 16px;
  padding: 0 4px;
  user-select: none;
}

@media (max-width: 720px) {
  .toolbar { flex-direction: column; align-items: stretch }
  .search-input { width: 100%; min-width: auto }
}
</style>
