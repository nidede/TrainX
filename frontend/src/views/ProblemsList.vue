<template>
  <div class="problems-page">
    <header class="page-header">
      <h1>结构化知识库</h1>
      <div class="controls">
        <input v-model="q" placeholder="按题名或标签搜索（回车不需提交）" />
        <select v-model="difficultyFilter">
          <option value="">全部难度</option>
          <option value="0">Lv0 入门</option>
          <option value="1">Lv1 简单</option>
          <option value="2">Lv2 较易</option>
          <option value="3">Lv3 中等</option>
          <option value="4">Lv4 较难</option>
          <option value="5">Lv5 困难</option>
          <option value="6">Lv6 极难</option>
        </select>
      </div>
    </header>

    <div v-if="loading" class="loading">加载中…</div>

    <div v-else>
      <div v-if="filtered.length === 0" class="empty">没有符合条件的题目。</div>

      <section class="grid">
        <article v-for="p in filtered" :key="p.id" class="card">
          <a :href="p.source_url" target="_blank" rel="noopener noreferrer" class="card-title">{{ p.title }}</a>
          <div class="meta">
            <span class="contest">{{ p.contest_name }}</span>
            <span class="dot">·</span>
            <span class="difficulty">Lv{{ p.unified_difficulty || '—' }}</span>
          </div>
          <div class="tags">
            <span v-for="t in p.tags" :key="t.id" class="tag">{{ t.name }}</span>
          </div>
        </article>
      </section>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import axios from 'axios'

const problems = ref([])
const loading = ref(false)
const q = ref('')
const difficultyFilter = ref('')

onMounted(async () => {
  loading.value = true
  try {
    const res = await axios.get('http://127.0.0.1:8000/api/problems/?limit=200')
    const data = res.data.results || res.data || []
    problems.value = data
  } catch (e) {
    console.error('获取题目列表失败', e)
  } finally {
    loading.value = false
  }
})

const filtered = computed(() => {
  const qv = q.value.trim().toLowerCase()
  return problems.value.filter(p => {
    if (difficultyFilter.value && p.unified_difficulty !== parseInt(difficultyFilter.value)) return false
    if (!qv) return true
    if ((p.title || '').toLowerCase().includes(qv)) return true
    if (p.tags && p.tags.some(t => (t.name || '').toLowerCase().includes(qv))) return true
    return false
  })
})
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
}
.page-header h1 {
  margin: 0;
  font-size: 40px;
  font-weight: 800;
}
.controls {
  display: flex;
  gap: 10px;
  align-items: center;
}
.controls input {
  min-width: 260px;
  padding: 10px 12px;
  border-radius: 10px;
  border: 1px solid rgba(255,255,255,0.06);
  background: rgba(255,255,255,0.02);
  color: #cbd5e1;
}
.controls select {
  padding: 10px 12px;
  border-radius: 10px;
  border: 1px solid rgba(255,255,255,0.06);
  background: rgba(255,255,255,0.02);
  color: #cbd5e1;
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
.card-title {
  font-size: 18px;
  font-weight: 700;
  color: #ffffff;
  text-decoration: none;
}
.meta { color: #94a3b8; font-size: 13px; margin-top: 8px }
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

@media (max-width: 720px) {
  .controls { flex-direction: column; align-items: stretch }
  .controls input { width: 100% }
}
</style>
