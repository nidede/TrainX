<template>
  <div class="user-center-page">
    <header class="page-header">
      <div class="header-left">
        <button class="back-button" @click="goBack">返回</button>
        <h1>个人中心</h1>
      </div>
    </header>

    <div v-if="loading" class="loading">加载中…</div>

    <div v-else>
      <!-- 用户信息 -->
      <section class="user-info">
        <div class="info-header">
          <div class="user-avatar">{{ (userInfo.username || '?')[0].toUpperCase() }}</div>
          <div>
            <h2>{{ userInfo.username }}</h2>
            <p class="user-subtitle">竞赛训练选手</p>
          </div>
        </div>
        <div class="info-grid">
          <div class="info-card">
            <div class="info-card__value">{{ userInfo.solved_problems_count || 0 }}</div>
            <div class="info-card__label">已解决</div>
          </div>
          <div class="info-card">
            <div class="info-card__value info-card__value--attempted">{{ userInfo.attempted_problems_count || 0 }}</div>
            <div class="info-card__label">尝试中</div>
          </div>
          <div class="info-card">
            <div class="info-card__value info-card__value--rate">{{ accuracy }}%</div>
            <div class="info-card__label">正确率</div>
          </div>
          <div class="info-card">
            <div class="info-card__value info-card__value--plans">{{ trainingPlansCount }}</div>
            <div class="info-card__label">训练计划</div>
          </div>
        </div>
      </section>

      <!-- 难度分布 -->
      <section v-if="difficultyDist.length > 0" class="section-card">
        <h2>难度分布</h2>
        <div class="dist-chart">
          <div v-for="d in difficultyDist" :key="d.level" class="dist-row">
            <span class="dist-label">Lv{{ d.level }}</span>
            <div class="dist-bar-bg">
              <div class="dist-bar-fill" :style="{ width: d.percent + '%' }" :class="`dist-fill--${d.level}`"></div>
            </div>
            <span class="dist-count">{{ d.count }}</span>
          </div>
        </div>
      </section>

      <!-- 训练计划 -->
      <section v-if="trainingPlans.length > 0" class="section-card">
        <h2>我的训练计划</h2>
        <div class="plans-list">
          <div v-for="plan in trainingPlans.slice(0, 3)" :key="plan.id" class="plan-item" @click="goToTrainingPlan">
            <div class="plan-item__head">
              <span class="plan-item__comp">{{ plan.target_competition }}</span>
              <span class="plan-item__award">{{ plan.target_award }}</span>
            </div>
            <div class="plan-item__meta">
              <span>{{ plan.duration_weeks }} 周</span>
              <span>每周 {{ plan.problems_per_week }} 题</span>
            </div>
          </div>
          <button v-if="trainingPlans.length > 3" class="plan-more" @click="goToTrainingPlan">查看全部 {{ trainingPlans.length }} 个计划</button>
        </div>
      </section>

      <!-- 做题记录 -->
      <section class="section-card">
        <div class="section-header">
          <h2>做题记录</h2>
          <select v-model="recordFilter" class="record-filter">
            <option value="all">全部</option>
            <option value="solved">已完成</option>
            <option value="unsolved">未完成</option>
          </select>
        </div>
        <div v-if="filteredProblems.length === 0" class="empty">暂无做题记录</div>
        <div v-else class="problems-list">
          <article v-for="up in filteredProblems" :key="up.id" :class="['problem-item', { 'problem-item--solved': up.solved }]">
            <a :href="up.problem.source_url" target="_blank" rel="noopener noreferrer" class="problem-title">{{ up.problem.title }}</a>
            <div class="problem-meta">
              <span class="contest">{{ up.problem.contest_name }}</span>
              <span class="dot">·</span>
              <span class="difficulty">Lv{{ up.problem.unified_difficulty || '—' }}</span>
              <span class="dot">·</span>
              <span :class="['status', up.solved ? 'solved' : 'unsolved']">
                {{ up.solved ? '已完成' : '尝试中' }}
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
import { useRouter } from 'vue-router'
import axios from 'axios'

const router = useRouter()
const userInfo = ref({})
const userProblems = ref([])
const trainingPlans = ref([])
const loading = ref(false)
const recordFilter = ref('all')

function goBack() {
  router.push('/home')
}

function goToTrainingPlan() {
  router.push('/training-plan')
}

onMounted(async () => {
  loading.value = true
  try {
    const [userRes, problemsRes, plansRes] = await Promise.all([
      axios.get('/api/users/center/'),
      axios.get('/api/users/problems/'),
      axios.get('/api/users/training-plans/'),
    ])
    userInfo.value = userRes.data
    userProblems.value = problemsRes.data.results || problemsRes.data || []
    trainingPlans.value = plansRes.data || []
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

const trainingPlansCount = computed(() => trainingPlans.value.length)

const filteredProblems = computed(() => {
  if (recordFilter.value === 'solved') return userProblems.value.filter(u => u.solved)
  if (recordFilter.value === 'unsolved') return userProblems.value.filter(u => !u.solved)
  return userProblems.value
})

const difficultyDist = computed(() => {
  const dist = {}
  for (let i = 0; i <= 6; i++) dist[i] = 0
  userProblems.value.forEach(up => {
    const d = up.problem.unified_difficulty
    if (d != null && d >= 0 && d <= 6) {
      dist[d]++
    }
  })
  const max = Math.max(...Object.values(dist), 1)
  return Object.entries(dist).map(([level, count]) => ({
    level: parseInt(level),
    count,
    percent: (count / max) * 100,
  }))
})
</script>

<style scoped>
.user-center-page {
  min-height: 100vh;
  padding: 32px 0;
  color: #e6eef8;
  background: radial-gradient(ellipse at 20% 0%, rgba(255,202,40,0.06), transparent 50%),
              radial-gradient(ellipse at 80% 100%, rgba(41,98,255,0.06), transparent 50%),
              #0b1120;
}
.page-header,
.user-info,
.section-card,
.loading {
  max-width: 1400px;
  margin-left: auto;
  margin-right: auto;
  padding-left: 48px;
  padding-right: 48px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 16px;
  margin-bottom: 24px;
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

.loading {
  padding: 40px;
  color: #94a3b8;
  text-align: center;
}

/* 用户信息卡片 */
.user-info {
  background: linear-gradient(135deg, rgba(255,202,40,0.06), rgba(41,98,255,0.06));
  border: 1px solid rgba(255,202,40,0.15);
  border-radius: 20px;
  padding: 28px;
  margin-bottom: 24px;
}
.info-header {
  display: flex;
  align-items: center;
  gap: 18px;
  margin-bottom: 24px;
}
.user-avatar {
  width: 56px;
  height: 56px;
  border-radius: 16px;
  background: linear-gradient(135deg, #ffca28, #ff5252);
  color: #111;
  display: grid;
  place-items: center;
  font-weight: 900;
  font-size: 24px;
  flex-shrink: 0;
}
.info-header h2 {
  margin: 0;
  font-size: 24px;
  font-weight: 800;
}
.user-subtitle {
  margin: 4px 0 0;
  color: #64748b;
  font-size: 14px;
}
.info-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 12px;
}
.info-card {
  text-align: center;
  padding: 18px 12px;
  border-radius: 14px;
  background: rgba(255,255,255,0.04);
  border: 1px solid rgba(255,255,255,0.06);
}
.info-card__value {
  font-size: 28px;
  font-weight: 900;
  color: #4ade80;
}
.info-card__value--attempted { color: #fbbf24; }
.info-card__value--rate { color: #60a5fa; }
.info-card__value--plans { color: #ffca28; }
.info-card__label {
  font-size: 12px;
  color: #64748b;
  margin-top: 4px;
}

/* 通用区域卡片 */
.section-card {
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 20px;
  padding: 24px;
  margin-bottom: 24px;
}
.section-card h2 {
  margin: 0 0 20px;
  font-size: 20px;
  font-weight: 700;
  color: #ffffff;
}
.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}
.section-header h2 {
  margin: 0;
}

/* 做题记录筛选 */
.record-filter {
  padding: 6px 14px;
  border-radius: 10px;
  border: 1px solid rgba(255,255,255,0.12);
  background: rgba(255,255,255,0.04);
  color: #cbd5e1;
  font-size: 13px;
  cursor: pointer;
  outline: none;
}
.record-filter option {
  background: #1a1f2e;
  color: #cbd5e1;
}

/* 难度分布图 */
.dist-chart {
  display: flex;
  flex-direction: column;
  gap: 10px;
}
.dist-row {
  display: flex;
  align-items: center;
  gap: 12px;
}
.dist-label {
  min-width: 30px;
  font-size: 12px;
  font-weight: 700;
  color: #94a3b8;
}
.dist-bar-bg {
  flex: 1;
  height: 8px;
  border-radius: 4px;
  background: rgba(255,255,255,0.06);
  overflow: hidden;
}
.dist-bar-fill {
  height: 100%;
  border-radius: 4px;
  transition: width 0.4s ease;
}
.dist-fill--0 { background: #94a3b8; }
.dist-fill--1 { background: #4ade80; }
.dist-fill--2 { background: #34d399; }
.dist-fill--3 { background: #fbbf24; }
.dist-fill--4 { background: #fb923c; }
.dist-fill--5 { background: #f87171; }
.dist-fill--6 { background: #ef4444; }
.dist-count {
  min-width: 24px;
  text-align: right;
  font-size: 13px;
  font-weight: 700;
  color: #cbd5e1;
}

/* 训练计划 */
.plans-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}
.plan-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  border-radius: 14px;
  background: rgba(255,255,255,0.04);
  border: 1px solid rgba(255,255,255,0.06);
  cursor: pointer;
  transition: all 0.2s ease;
}
.plan-item:hover {
  background: rgba(255,255,255,0.07);
  border-color: rgba(255,202,40,0.25);
}
.plan-item__head {
  display: flex;
  align-items: center;
  gap: 10px;
}
.plan-item__comp {
  font-weight: 700;
  color: #fff;
}
.plan-item__award {
  padding: 2px 10px;
  border-radius: 10px;
  background: rgba(255,202,40,0.12);
  color: #ffca28;
  font-size: 12px;
  font-weight: 700;
}
.plan-item__meta {
  display: flex;
  gap: 16px;
  color: #64748b;
  font-size: 13px;
}
.plan-more {
  padding: 10px;
  border-radius: 10px;
  border: 1px dashed rgba(255,255,255,0.1);
  background: transparent;
  color: #64748b;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.15s;
}
.plan-more:hover {
  background: rgba(255,255,255,0.04);
  color: #94a3b8;
}

/* 做题记录列表 */
.empty {
  padding: 40px;
  color: #94a3b8;
  text-align: center;
}

.problems-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.problem-item {
  padding: 16px 20px;
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(255, 255, 255, 0.06);
  transition: transform 150ms ease, box-shadow 150ms ease;
}
.problem-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.4);
}
.problem-item--solved {
  border-color: rgba(74, 222, 128, 0.2);
  background: rgba(74, 222, 128, 0.03);
}

.problem-title {
  font-size: 16px;
  font-weight: 700;
  color: #ffffff;
  text-decoration: none;
  display: block;
  margin-bottom: 8px;
}

.problem-meta {
  color: #94a3b8;
  font-size: 13px;
  margin-bottom: 10px;
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
  color: #fbbf24;
}

.problem-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.tag {
  display: inline-block;
  background: rgba(99, 102, 241, 0.12);
  color: #c7d2fe;
  padding: 4px 10px;
  border-radius: 14px;
  font-size: 12px;
}

@media (max-width: 720px) {
  .info-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}
</style>
