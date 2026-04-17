<template>
  <div class="user-center-page">
    <header class="page-header">
      <h1>个人中心</h1>
    </header>

    <div v-if="loading" class="loading">加载中…</div>

    <div v-else>
      <section class="user-info">
        <h2>用户信息</h2>
        <div class="info-grid">
          <div class="info-item">
            <span class="label">用户名:</span>
            <span class="value">{{ userInfo.username }}</span>
          </div>
          <div class="info-item">
            <span class="label">已解决题目:</span>
            <span class="value">{{ userInfo.solved_problems_count || 0 }}</span>
          </div>
          <div class="info-item">
            <span class="label">尝试题目:</span>
            <span class="value">{{ userInfo.attempted_problems_count || 0 }}</span>
          </div>
          <div class="info-item">
            <span class="label">正确率:</span>
            <span class="value">{{ accuracy }}%</span>
          </div>
        </div>
      </section>

      <section class="user-problems">
        <h2>做题记录</h2>
        <div v-if="userProblems.length === 0" class="empty">暂无做题记录</div>
        <div v-else class="problems-list">
          <article v-for="up in userProblems" :key="up.id" class="problem-item">
            <a :href="up.problem.source_url" target="_blank" rel="noopener noreferrer" class="problem-title">{{ up.problem.title }}</a>
            <div class="problem-meta">
              <span class="contest">{{ up.problem.contest_name }}</span>
              <span class="dot">·</span>
              <span class="difficulty">Lv{{ up.problem.unified_difficulty || '—' }}</span>
              <span class="dot">·</span>
              <span :class="['status', up.solved ? 'solved' : 'unsolved']">
                {{ up.solved ? '已解决' : '未解决' }}
              </span>
            </div>
            <div class="problem-tags">
              <span v-for="t in up.problem.tags" :key="t.id" class="tag">{{ t.name }}</span>
            </div>
          </article>
        </div>
      </section>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import axios from 'axios'

const userInfo = ref({})
const userProblems = ref([])
const loading = ref(false)

onMounted(async () => {
  loading.value = true
  try {
    // 获取用户信息
    const userRes = await axios.get('/api/users/center/')
    userInfo.value = userRes.data

    // 获取用户做题记录
    const problemsRes = await axios.get('/api/users/problems/')
    userProblems.value = problemsRes.data
  } catch (e) {
    console.error('获取用户信息失败', e)
  } finally {
    loading.value = false
  }
})

const accuracy = computed(() => {
  const solved = userInfo.value.solved_problems_count || 0
  const attempted = userInfo.value.attempted_problems_count || 0
  return attempted > 0 ? Math.round((solved / attempted) * 100) : 0
})
</script>

<style scoped>
.user-center-page {
  padding: 28px 20px;
  max-width: 1100px;
  margin: 0 auto;
  color: #e6eef8;
}

.page-header {
  margin-bottom: 32px;
}

.page-header h1 {
  margin: 0;
  font-size: 40px;
  font-weight: 800;
}

.loading {
  padding: 40px;
  color: #94a3b8;
  text-align: center;
}

.user-info {
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 20px;
  padding: 24px;
  margin-bottom: 32px;
}

.user-info h2 {
  margin-top: 0;
  margin-bottom: 20px;
  font-size: 24px;
  color: #ffffff;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
}

.info-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 12px;
}

.label {
  color: #94a3b8;
  font-size: 14px;
}

.value {
  color: #ffffff;
  font-weight: 700;
  font-size: 16px;
}

.user-problems {
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 20px;
  padding: 24px;
}

.user-problems h2 {
  margin-top: 0;
  margin-bottom: 20px;
  font-size: 24px;
  color: #ffffff;
}

.empty {
  padding: 40px;
  color: #94a3b8;
  text-align: center;
}

.problems-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.problem-item {
  padding: 18px;
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.08);
  transition: transform 150ms ease, box-shadow 150ms ease;
}

.problem-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.4);
}

.problem-title {
  font-size: 18px;
  font-weight: 700;
  color: #ffffff;
  text-decoration: none;
  display: block;
  margin-bottom: 8px;
}

.problem-meta {
  color: #94a3b8;
  font-size: 13px;
  margin-bottom: 12px;
}

.dot {
  margin: 0 8px;
}

.status {
  font-weight: 600;
}

.status.solved {
  color: #4ade80;
}

.status.unsolved {
  color: #f87171;
}

.problem-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.tag {
  display: inline-block;
  background: rgba(99, 102, 241, 0.12);
  color: #c7d2fe;
  padding: 6px 10px;
  border-radius: 16px;
  font-size: 12px;
}

@media (max-width: 720px) {
  .info-grid {
    grid-template-columns: 1fr;
  }
}
</style>