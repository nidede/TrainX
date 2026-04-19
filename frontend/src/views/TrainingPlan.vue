<template>
  <div class="tp-page">
    <!-- 页面头部 -->
    <header class="tp-header">
      <button class="tp-back" @click="goBack">
        <span class="tp-back-arrow">←</span> 返回首页
      </button>
      <div class="tp-hero">
        <div class="tp-hero-icon">T</div>
        <div>
          <h1 class="tp-hero-title">智能训练计划</h1>
          <p class="tp-hero-sub">选择基础 · 锁定目标 · 生成专属题单</p>
        </div>
      </div>
    </header>

    <!-- ━━ 我的训练计划 ━━ -->
    <div v-if="!generatedPlan && !viewingPlan" class="tp-saved">
      <div class="tp-section-bar">
        <h2>我的训练计划</h2>
        <button v-if="!showWizard && savedPlans.length > 0" class="tp-btn tp-btn--outline tp-btn--sm" @click="showWizard = true">+ 新建计划</button>
      </div>

      <div v-if="savedPlans.length === 0" class="tp-empty">
        <div class="tp-empty-icon">📋</div>
        <p>还没有训练计划</p>
        <span>在下方选择你的基础和目标，生成你的第一个专属训练计划</span>
      </div>

      <div v-else class="tp-plans-grid">
        <div v-for="plan in savedPlans" :key="plan.id" class="tp-plan-card" @click="viewPlan(plan)">
          <div class="tp-plan-card__head">
            <span class="tp-plan-card__comp">{{ plan.target_competition }}</span>
            <span class="tp-plan-card__award">{{ plan.target_award }}</span>
          </div>
          <div class="tp-plan-card__meta">
            <span><b>Lv{{ plan.current_level }}</b> → <b>Lv{{ plan.plan_data?.target_difficulty || '—' }}</b></span>
            <span>{{ plan.duration_weeks }} 周</span>
            <span>每周 {{ plan.problems_per_week }} 题</span>
          </div>
          <div class="tp-plan-card__tags">
            <span v-for="tag in (plan.plan_data?.key_tags || []).slice(0, 4)" :key="tag" class="tp-plan-card__tag">{{ tag }}</span>
          </div>
          <div class="tp-plan-card__foot">
            <span class="tp-plan-card__date">{{ formatDate(plan.created_at) }}</span>
            <button class="tp-plan-card__del" @click.stop="deletePlan(plan.id)">删除</button>
          </div>
        </div>
      </div>
    </div>

    <!-- ━━ 向导 ━━ -->
    <div v-if="!generatedPlan && !viewingPlan && (showWizard || savedPlans.length === 0)" class="tp-wizard">
      <!-- 进度条 -->
      <div class="tp-progress">
        <div v-for="i in 3" :key="i" :class="['tp-progress__dot', { active: step >= i, current: step === i }]">
          <span class="tp-progress__num">{{ i }}</span>
        </div>
        <div class="tp-progress__line"><div class="tp-progress__fill" :style="{ width: ((step - 1) / 2 * 100) + '%' }"></div></div>
      </div>

      <!-- Step 1 -->
      <div v-if="step === 1" class="tp-step">
        <h2 class="tp-step__title">选择你的当前水平</h2>
        <p class="tp-step__desc">根据你的算法基础选择最接近的等级</p>
        <div class="tp-levels">
          <div
            v-for="lv in levels"
            :key="lv.value"
            :class="['tp-level', { selected: form.currentLevel === lv.value }]"
            @click="form.currentLevel = lv.value"
          >
            <div class="tp-level__badge">Lv{{ lv.value }}</div>
            <div class="tp-level__desc">{{ lv.description }}</div>
          </div>
        </div>
        <div class="tp-step__actions">
          <button class="tp-btn tp-btn--primary" :disabled="form.currentLevel === null" @click="step = 2">下一步</button>
        </div>
      </div>

      <!-- Step 2 -->
      <div v-if="step === 2" class="tp-step">
        <h2 class="tp-step__title">选择目标赛事</h2>
        <p class="tp-step__desc">选择你要备战的竞赛</p>
        <div class="tp-comps">
          <div
            v-for="(comp, key) in competitions"
            :key="key"
            :class="['tp-comp', { selected: form.competition === key }]"
            @click="selectCompetition(key)"
          >
            <div class="tp-comp__name">{{ comp.name }}</div>
            <div class="tp-comp__full">{{ comp.full_name }}</div>
          </div>
        </div>
        <div class="tp-step__actions">
          <button class="tp-btn tp-btn--ghost" @click="step = 1">上一步</button>
          <button class="tp-btn tp-btn--primary" :disabled="!form.competition" @click="step = 3">下一步</button>
        </div>
      </div>

      <!-- Step 3 -->
      <div v-if="step === 3" class="tp-step">
        <h2 class="tp-step__title">选择目标奖项</h2>
        <p class="tp-step__desc">根据你的期望选择奖项等级</p>
        <div class="tp-awards">
          <button
            v-for="award in currentAwards"
            :key="award"
            :class="['tp-award', { selected: form.award === award }]"
            @click="form.award = award"
          >{{ award }}</button>
        </div>
        <div class="tp-step__actions">
          <button class="tp-btn tp-btn--ghost" @click="step = 2">上一步</button>
          <button class="tp-btn tp-btn--generate" :disabled="!form.award || generating" @click="generatePlan">
            {{ generating ? '生成中…' : '生成训练计划' }}
          </button>
        </div>
      </div>
    </div>

    <!-- ━━ 计划详情 / 生成预览 ━━ -->
    <div v-if="generatedPlan || viewingPlan" class="tp-result">
      <div class="tp-top-bar">
        <button class="tp-back" @click="backToList">← 返回计划列表</button>
        <button :class="['tp-toggle-tags', { active: tpShowTags }]" @click="tpShowTags = !tpShowTags">
          {{ tpShowTags ? '隐藏知识点' : '显示知识点' }}
        </button>
      </div>

      <!-- 概览卡片 -->
      <div class="tp-overview">
        <div class="tp-overview__top">
          <div class="tp-overview__head">
            <h2>{{ displayPlan.target_competition }} · {{ displayPlan.target_award }}</h2>
            <p class="tp-overview__summary">{{ displayPlan.plan_data.summary }}</p>
          </div>
          <div class="tp-overview__stats">
            <div class="tp-stat">
              <div class="tp-stat__val">{{ displayPlan.duration_weeks }}</div>
              <div class="tp-stat__label">训练周数</div>
            </div>
            <div class="tp-stat">
              <div class="tp-stat__val">{{ displayPlan.problems_per_week }}</div>
              <div class="tp-stat__label">每周题量</div>
            </div>
            <div class="tp-stat">
              <div class="tp-stat__val">Lv{{ displayPlan.plan_data.target_difficulty }}</div>
              <div class="tp-stat__label">目标难度</div>
            </div>
            <div class="tp-stat">
              <div class="tp-stat__val">{{ totalProblems }}</div>
              <div class="tp-stat__label">总题量</div>
            </div>
          </div>
        </div>
        <div class="tp-overview__tags">
          <span class="tp-overview__tags-label">核心知识点</span>
          <span v-for="tag in displayPlan.plan_data.key_tags" :key="tag" class="tp-otag">{{ tag }}</span>
        </div>
      </div>

      <!-- 训练阶段 -->
      <div v-for="phase in displayPlan.plan_data.phases" :key="phase.key" class="tp-phase">
        <div :class="['tp-phase__header', `tp-phase__header--${phase.key}`]">
          <span class="tp-phase__icon">{{ phaseIcon(phase.key) }}</span>
          <div>
            <h3>{{ phase.name }}</h3>
            <p>{{ phase.description }}</p>
          </div>
        </div>

        <div v-for="week in phase.weeks" :key="week.week" class="tp-week">
          <div class="tp-week__header" @click="toggleWeek(week.week)">
            <div class="tp-week__left">
              <span class="tp-week__num">W{{ week.week }}</span>
              <span class="tp-week__theme">{{ week.theme }}</span>
              <span class="tp-week__diff">Lv{{ week.difficulty_range[0] }}–Lv{{ week.difficulty_range[1] }}</span>
            </div>
            <span :class="['tp-week__arrow', { open: expandedWeeks[week.week] }]">▾</span>
          </div>
          <div v-if="expandedWeeks[week.week]" class="tp-week__body">
            <div v-if="week.problems.length === 0" class="tp-week__empty">暂无匹配题目，请先导入题库数据</div>
            <div
              v-for="p in week.problems"
              :key="p.id"
              :class="['tp-problem', { 'tp-problem--solved': isSolved(p.id), 'tp-problem--attempted': isAttempted(p.id) }]"
            >
              <div class="tp-problem__check">
                <input type="checkbox" :id="`tp-p-${p.id}`" :checked="isSolved(p.id)" @change="toggleStatus(p.id)" />
                <label :for="`tp-p-${p.id}`"></label>
              </div>
              <router-link :to="`/problems/${p.id}`" class="tp-problem__main" @click="markAsAttempted(p.id)">
                <span class="tp-problem__diff">Lv{{ p.difficulty || '—' }}</span>
                <span class="tp-problem__title">{{ p.title }}</span>
                <span v-if="tpShowTags" class="tp-problem__tags">
                  <span v-for="t in p.tags.slice(0, 3)" :key="t" class="tp-problem__tag">{{ t }}</span>
                </span>
              </router-link>
              <span :class="['tp-problem__status', getStatusClass(p.id)]">{{ getStatusText(p.id) }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- 操作栏 -->
      <div class="tp-result__actions">
        <template v-if="generatedPlan && !viewingPlan">
          <template v-if="planSaved">
            <span class="tp-saved-badge">✓ 已保存</span>
            <button class="tp-btn tp-btn--primary" @click="goToProblems">前往知识库刷题</button>
          </template>
          <template v-else>
            <button class="tp-btn tp-btn--confirm" :disabled="saving" @click="savePlan">
              {{ saving ? '保存中…' : '确认保存此计划' }}
            </button>
            <button class="tp-btn tp-btn--ghost" @click="resetForm">重新生成</button>
          </template>
        </template>
        <template v-if="viewingPlan">
          <button class="tp-btn tp-btn--primary" @click="goToProblems">前往知识库刷题</button>
          <button class="tp-btn tp-btn--danger" @click="deleteAndViewingPlan">删除此计划</button>
        </template>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'

const router = useRouter()

const step = ref(1)
const generating = ref(false)
const saving = ref(false)
const planSaved = ref(false)
const generatedPlan = ref(null)
const viewingPlan = ref(null)
const showWizard = ref(false)
const savedPlans = ref([])
const expandedWeeks = reactive({})
const problemStatus = ref({})
const tpShowTags = ref(true)

const form = reactive({
  currentLevel: null,
  competition: '',
  award: '',
})

const levels = ref([])
const competitions = ref({})

const selectedLevelDesc = computed(() => {
  const lv = levels.value.find(l => l.value === form.currentLevel)
  return lv ? lv.description : ''
})

const currentAwards = computed(() => {
  const comp = competitions.value[form.competition]
  return comp ? comp.awards : []
})

const displayPlan = computed(() => {
  return viewingPlan.value || generatedPlan.value
})

const totalProblems = computed(() => {
  const plan = displayPlan.value
  if (!plan) return 0
  let total = 0
  for (const phase of plan.plan_data.phases) {
    for (const week of phase.weeks) {
      total += week.problems.length
    }
  }
  return total
})

function formatDate(dateStr) {
  if (!dateStr) return ''
  const d = new Date(dateStr)
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`
}

function selectCompetition(key) {
  form.competition = key
  form.award = ''
}

function toggleWeek(weekNum) {
  expandedWeeks[weekNum] = !expandedWeeks[weekNum]
}

function phaseIcon(key) {
  if (key === 'foundation') return 'I'
  if (key === 'core') return 'II'
  return 'III'
}

async function fetchConfig() {
  try {
    const res = await axios.get('/api/users/competition-config/')
    levels.value = res.data.levels
    competitions.value = res.data.competitions
  } catch (e) {
    console.error('获取赛事配置失败', e)
  }
}

async function fetchSavedPlans() {
  try {
    const res = await axios.get('/api/users/training-plans/')
    savedPlans.value = res.data || []
  } catch (e) {
    console.error('获取已保存计划失败', e)
  }
}

async function generatePlan() {
  generating.value = true
  try {
    const res = await axios.post('/api/users/training-plans/generate/', {
      current_level: form.currentLevel,
      competition: form.competition,
      award: form.award,
    })
    generatedPlan.value = res.data
    planSaved.value = false
    for (const phase of res.data.plan_data.phases) {
      for (const week of phase.weeks) {
        expandedWeeks[week.week] = true
      }
    }
  } catch (e) {
    console.error('生成训练计划失败', e)
    alert(e.response?.data?.msg || '生成失败，请稍后重试')
  } finally {
    generating.value = false
  }
}

async function savePlan() {
  saving.value = true
  try {
    await axios.post('/api/users/training-plans/save/', {
      current_level: form.currentLevel,
      competition: form.competition,
      award: form.award,
    })
    planSaved.value = true
    fetchSavedPlans()
  } catch (e) {
    console.error('保存训练计划失败', e)
    alert(e.response?.data?.msg || '保存失败，请稍后重试')
  } finally {
    saving.value = false
  }
}

async function deletePlan(planId) {
  if (!confirm('确定删除此训练计划？')) return
  try {
    await axios.delete(`/api/users/training-plans/${planId}/`)
    fetchSavedPlans()
  } catch (e) {
    console.error('删除计划失败', e)
  }
}

async function deleteAndViewingPlan() {
  if (!viewingPlan.value) return
  if (!confirm('确定删除此训练计划？')) return
  try {
    await axios.delete(`/api/users/training-plans/${viewingPlan.value.id}/`)
    viewingPlan.value = null
    fetchSavedPlans()
  } catch (e) {
    console.error('删除计划失败', e)
  }
}

function viewPlan(plan) {
  viewingPlan.value = plan
  for (const key in expandedWeeks) {
    delete expandedWeeks[key]
  }
  if (plan.plan_data?.phases) {
    for (const phase of plan.plan_data.phases) {
      for (const week of phase.weeks) {
        expandedWeeks[week.week] = true
      }
    }
  }
}

function backToList() {
  viewingPlan.value = null
  generatedPlan.value = null
}

function resetForm() {
  step.value = 1
  form.currentLevel = null
  form.competition = ''
  form.award = ''
  generatedPlan.value = null
  planSaved.value = false
}

function goBack() {
  router.push('/home')
}

function goToProblems() {
  router.push('/problems')
}

// 用户做题记录
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

async function markAsAttempted(problemId) {
  if (!problemStatus.value[problemId]) {
    problemStatus.value[problemId] = { solved: false, attempted: true }
    try {
      await axios.post('/api/users/problems/', { problem_id: problemId, solved: false })
    } catch (e) {
      // 回滚本地状态
      delete problemStatus.value[problemId]
      console.error('保存题目状态失败', e)
    }
  }
}

async function toggleStatus(problemId) {
  const current = problemStatus.value[problemId] || { solved: false, attempted: false }
  const newSolved = !current.solved
  const oldStatus = { ...current }
  problemStatus.value[problemId] = { solved: newSolved, attempted: true }
  try {
    await axios.post('/api/users/problems/', { problem_id: problemId, solved: newSolved })
  } catch (e) {
    // 回滚本地状态
    problemStatus.value[problemId] = oldStatus
    console.error('保存题目状态失败', e)
  }
}

function isSolved(problemId) {
  return problemStatus.value[problemId]?.solved || false
}

function isAttempted(problemId) {
  return problemStatus.value[problemId]?.attempted || false
}

function getStatusText(problemId) {
  const s = problemStatus.value[problemId]
  if (!s) return '未做'
  if (s.solved) return '已完成'
  return '尝试中'
}

function getStatusClass(problemId) {
  const s = problemStatus.value[problemId]
  if (!s) return 'tp-status--none'
  if (s.solved) return 'tp-status--solved'
  return 'tp-status--attempted'
}

onMounted(() => {
  fetchConfig()
  fetchSavedPlans()
  fetchUserProblems()
})
</script>

<style scoped>
/* ━━ 全局 ━━ */
.tp-page {
  min-height: 100vh;
  padding: 0 0 60px;
  color: #e2e8f0;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", sans-serif;
  background: radial-gradient(ellipse at 20% 0%, rgba(255,202,40,0.08), transparent 50%),
              radial-gradient(ellipse at 80% 100%, rgba(41,98,255,0.08), transparent 50%),
              #0b1120;
}

/* ━━ 头部 ━━ */
.tp-header {
  padding: 24px 48px 0;
  max-width: 1400px;
  margin: 0 auto;
}
.tp-back {
  background: none;
  border: none;
  color: #64748b;
  font-size: 13px;
  cursor: pointer;
  padding: 0 0 18px;
  transition: color 0.15s;
}
.tp-back:hover { color: #94a3b8; }
.tp-back-arrow { margin-right: 4px; }

.tp-hero {
  display: flex;
  align-items: center;
  gap: 18px;
  margin-bottom: 32px;
}
.tp-hero-icon {
  width: 52px; height: 52px;
  border-radius: 16px;
  background: linear-gradient(135deg, #ffca28, #ff5252);
  color: #111;
  display: grid; place-items: center;
  font-weight: 900; font-size: 22px;
  flex-shrink: 0;
  box-shadow: 0 4px 20px rgba(255,202,40,0.25);
}
.tp-hero-title {
  margin: 0;
  font-size: 28px;
  font-weight: 800;
  letter-spacing: -0.5px;
}
.tp-hero-sub {
  margin: 4px 0 0;
  color: #64748b;
  font-size: 14px;
  letter-spacing: 0.5px;
}

/* ━━ 通用按钮 ━━ */
.tp-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 11px 24px;
  border-radius: 12px;
  font-weight: 700;
  font-size: 14px;
  cursor: pointer;
  border: none;
  transition: all 0.2s ease;
}
.tp-btn:disabled { opacity: 0.35; cursor: not-allowed; }
.tp-btn--sm { padding: 7px 16px; font-size: 13px; border-radius: 10px; }
.tp-btn--primary {
  background: linear-gradient(135deg, #ffca28, #ff8a25);
  color: #111;
  box-shadow: 0 4px 16px rgba(255,202,40,0.2);
}
.tp-btn--primary:hover:not(:disabled) { box-shadow: 0 6px 24px rgba(255,202,40,0.35); transform: translateY(-1px); }
.tp-btn--generate {
  background: linear-gradient(135deg, #ff5252, #2962ff);
  color: #fff;
  box-shadow: 0 4px 16px rgba(41,98,255,0.25);
}
.tp-btn--generate:hover:not(:disabled) { box-shadow: 0 6px 24px rgba(41,98,255,0.4); transform: translateY(-1px); }
.tp-btn--confirm {
  background: linear-gradient(135deg, #34d399, #10b981);
  color: #111;
  box-shadow: 0 4px 16px rgba(16,185,129,0.25);
}
.tp-btn--confirm:hover:not(:disabled) { box-shadow: 0 6px 24px rgba(16,185,129,0.4); transform: translateY(-1px); }
.tp-btn--ghost {
  background: transparent;
  border: 1px solid rgba(255,255,255,0.12);
  color: #94a3b8;
}
.tp-btn--ghost:hover { background: rgba(255,255,255,0.05); color: #cbd5e1; }
.tp-btn--outline {
  background: rgba(255,255,255,0.06);
  border: 1px solid rgba(255,255,255,0.15);
  color: #cbd5e1;
}
.tp-btn--outline:hover { background: rgba(255,255,255,0.1); }
.tp-btn--danger {
  background: rgba(239,68,68,0.1);
  border: 1px solid rgba(239,68,68,0.25);
  color: #fca5a5;
}
.tp-btn--danger:hover { background: rgba(239,68,68,0.18); }

/* ━━ 已保存计划 ━━ */
.tp-saved { max-width: 1400px; margin: 0 auto; padding: 0 48px; }
.tp-section-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 18px;
}
.tp-section-bar h2 { margin: 0; font-size: 20px; font-weight: 700; }
.tp-empty {
  text-align: center;
  padding: 48px 24px;
  border-radius: 20px;
  background: rgba(255,255,255,0.02);
  border: 1px dashed rgba(255,255,255,0.08);
  margin-bottom: 28px;
}
.tp-empty-icon { font-size: 36px; margin-bottom: 12px; }
.tp-empty p { color: #94a3b8; margin: 0 0 6px; font-size: 16px; font-weight: 600; }
.tp-empty span { color: #475569; font-size: 13px; }
.tp-plans-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 16px;
  margin-bottom: 32px;
}
.tp-plan-card {
  padding: 22px;
  border-radius: 16px;
  background: rgba(255,255,255,0.03);
  border: 1px solid rgba(255,255,255,0.06);
  cursor: pointer;
  transition: all 0.2s ease;
}
.tp-plan-card:hover {
  background: rgba(255,255,255,0.06);
  border-color: rgba(255,202,40,0.3);
  box-shadow: 0 8px 32px rgba(0,0,0,0.3);
  transform: translateY(-2px);
}
.tp-plan-card__head { display: flex; align-items: center; gap: 10px; margin-bottom: 12px; }
.tp-plan-card__comp { font-weight: 800; font-size: 18px; color: #fff; }
.tp-plan-card__award {
  padding: 3px 10px; border-radius: 10px;
  background: rgba(255,202,40,0.12); color: #ffca28;
  font-size: 12px; font-weight: 700;
}
.tp-plan-card__meta { display: flex; gap: 16px; color: #64748b; font-size: 13px; margin-bottom: 12px; }
.tp-plan-card__meta b { color: #94a3b8; font-weight: 600; }
.tp-plan-card__tags { display: flex; flex-wrap: wrap; gap: 6px; margin-bottom: 14px; }
.tp-plan-card__tag {
  padding: 3px 10px; border-radius: 8px;
  background: rgba(255,255,255,0.04); color: #64748b; font-size: 11px;
}
.tp-plan-card__foot { display: flex; justify-content: space-between; align-items: center; }
.tp-plan-card__date { color: #334155; font-size: 12px; }
.tp-plan-card__del {
  padding: 4px 12px; border-radius: 8px;
  border: 1px solid rgba(239,68,68,0.2); background: transparent;
  color: #ef4444; font-size: 12px; cursor: pointer; transition: all 0.15s;
}
.tp-plan-card__del:hover { background: rgba(239,68,68,0.1); }

/* ━━ 向导 ━━ */
.tp-wizard { max-width: 1400px; margin: 0 auto; padding: 0 48px; }

/* 进度条 */
.tp-progress {
  display: flex; align-items: center; justify-content: center;
  gap: 0; margin-bottom: 36px; position: relative;
}
.tp-progress__line {
  position: absolute; top: 50%; left: calc(50% - 80px); width: 160px;
  height: 2px; background: rgba(255,255,255,0.06); transform: translateY(-50%);
}
.tp-progress__fill {
  height: 100%; background: linear-gradient(90deg, #ffca28, #ff5252);
  transition: width 0.4s ease; border-radius: 2px;
}
.tp-progress__dot {
  width: 36px; height: 36px; border-radius: 50%;
  display: grid; place-items: center;
  background: rgba(255,255,255,0.06);
  border: 2px solid rgba(255,255,255,0.1);
  color: #475569; font-weight: 800; font-size: 13px;
  transition: all 0.3s ease; z-index: 1;
  margin: 0 62px;
}
.tp-progress__dot.active {
  border-color: #ffca28;
  background: rgba(255,202,40,0.1);
  color: #ffca28;
}
.tp-progress__dot.current {
  border-color: #ffca28;
  background: linear-gradient(135deg, #ffca28, #ff8a25);
  color: #111;
  box-shadow: 0 0 20px rgba(255,202,40,0.3);
}

/* 步骤内容 */
.tp-step { animation: fadeIn 0.25s ease; }
.tp-step__title { margin: 0 0 6px; font-size: 22px; font-weight: 800; text-align: center; }
.tp-step__desc { margin: 0 0 24px; color: #64748b; font-size: 14px; text-align: center; }
.tp-step__actions { display: flex; justify-content: center; gap: 12px; margin-top: 28px; }

/* 水平卡片 */
.tp-levels {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(190px, 1fr));
  gap: 10px;
}
.tp-level {
  padding: 16px 18px; border-radius: 14px;
  border: 1px solid rgba(255,255,255,0.06);
  background: rgba(255,255,255,0.02);
  cursor: pointer; transition: all 0.2s ease;
}
.tp-level:hover { background: rgba(255,255,255,0.05); border-color: rgba(255,255,255,0.12); }
.tp-level.selected {
  background: rgba(255,202,40,0.08);
  border-color: rgba(255,202,40,0.4);
  box-shadow: 0 0 24px rgba(255,202,40,0.08);
}
.tp-level__badge {
  font-size: 20px; font-weight: 900; color: #ffca28; margin-bottom: 6px;
}
.tp-level.selected .tp-level__badge { color: #fff; }
.tp-level__desc { font-size: 13px; color: #64748b; line-height: 1.5; }

/* 赛事卡片 */
.tp-comps {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(190px, 1fr));
  gap: 10px;
}
.tp-comp {
  padding: 20px; border-radius: 14px;
  border: 1px solid rgba(255,255,255,0.06);
  background: rgba(255,255,255,0.02);
  cursor: pointer; transition: all 0.2s ease;
}
.tp-comp:hover { background: rgba(255,255,255,0.05); border-color: rgba(255,255,255,0.12); }
.tp-comp.selected {
  background: rgba(41,98,255,0.08);
  border-color: rgba(41,98,255,0.4);
  box-shadow: 0 0 24px rgba(41,98,255,0.08);
}
.tp-comp__name { font-size: 20px; font-weight: 800; color: #fff; margin-bottom: 6px; }
.tp-comp.selected .tp-comp__name { color: #93c5fd; }
.tp-comp__full { font-size: 12px; color: #64748b; line-height: 1.4; }

/* 奖项按钮 */
.tp-awards { display: flex; flex-wrap: wrap; gap: 10px; justify-content: center; }
.tp-award {
  padding: 10px 22px; border-radius: 12px;
  border: 1px solid rgba(255,255,255,0.08);
  background: rgba(255,255,255,0.03);
  color: #94a3b8; font-size: 14px; font-weight: 600;
  cursor: pointer; transition: all 0.2s ease;
}
.tp-award:hover { background: rgba(255,255,255,0.06); border-color: rgba(255,255,255,0.15); }
.tp-award.selected {
  background: rgba(255,202,40,0.1);
  border-color: rgba(255,202,40,0.45);
  color: #ffca28;
  box-shadow: 0 0 16px rgba(255,202,40,0.1);
}

/* ━━ 计划结果 ━━ */
.tp-result { max-width: 1400px; margin: 0 auto; padding: 0 48px; }

/* 概览 */
.tp-overview {
  padding: 22px 28px; border-radius: 16px;
  background: linear-gradient(135deg, rgba(255,202,40,0.06) 0%, rgba(41,98,255,0.06) 100%);
  border: 1px solid rgba(255,202,40,0.15);
  margin-bottom: 28px;
  box-shadow: 0 8px 40px rgba(0,0,0,0.2);
}
.tp-overview__top {
  display: flex;
  align-items: center;
  gap: 24px;
  margin-bottom: 14px;
}
.tp-overview__head { flex: 1; min-width: 0; }
.tp-overview__head h2 { margin: 0 0 4px; font-size: 20px; font-weight: 800; }
.tp-overview__summary { color: #94a3b8; margin: 0; font-size: 13px; line-height: 1.6; }
.tp-overview__stats {
  display: flex;
  gap: 10px;
  flex-shrink: 0;
}
.tp-stat {
  text-align: center; padding: 10px 16px;
  border-radius: 10px;
  background: rgba(255,255,255,0.04);
  border: 1px solid rgba(255,255,255,0.06);
}
.tp-stat__val {
  font-size: 22px; font-weight: 900;
  background: linear-gradient(135deg, #ffca28, #ff8a25);
  -webkit-background-clip: text; -webkit-text-fill-color: transparent;
  background-clip: text;
}
.tp-stat__label { font-size: 11px; color: #64748b; margin-top: 2px; }
.tp-overview__tags { display: flex; flex-wrap: wrap; align-items: center; gap: 8px; }
.tp-overview__tags-label { color: #475569; font-size: 13px; font-weight: 600; margin-right: 4px; }
.tp-otag {
  padding: 4px 12px; border-radius: 12px;
  background: rgba(41,98,255,0.1); border: 1px solid rgba(41,98,255,0.2);
  color: #93c5fd; font-size: 12px; font-weight: 500;
}

/* 阶段 */
.tp-phase { margin-bottom: 28px; }
.tp-phase__header {
  display: flex; align-items: center; gap: 14px;
  padding: 16px 22px; border-radius: 14px; margin-bottom: 4px;
}
.tp-phase__header h3 { margin: 0; font-size: 16px; font-weight: 700; }
.tp-phase__header p { margin: 2px 0 0; color: #64748b; font-size: 12px; }
.tp-phase__icon {
  width: 38px; height: 38px; border-radius: 10px;
  display: grid; place-items: center;
  font-weight: 800; font-size: 14px; flex-shrink: 0;
}
.tp-phase__header--foundation {
  background: rgba(52,211,153,0.08); border: 1px solid rgba(52,211,153,0.2);
}
.tp-phase__header--foundation .tp-phase__icon { background: rgba(52,211,153,0.15); color: #34d399; }
.tp-phase__header--core {
  background: rgba(59,130,246,0.08); border: 1px solid rgba(59,130,246,0.2);
}
.tp-phase__header--core .tp-phase__icon { background: rgba(59,130,246,0.15); color: #3b82f6; }
.tp-phase__header--sprint {
  background: rgba(239,68,68,0.08); border: 1px solid rgba(239,68,68,0.2);
}
.tp-phase__header--sprint .tp-phase__icon { background: rgba(239,68,68,0.15); color: #ef4444; }

/* 周 */
.tp-week {
  border: 1px solid rgba(255,255,255,0.04);
  border-top: none;
  background: rgba(255,255,255,0.01);
}
.tp-week:first-of-type { border-top: 1px solid rgba(255,255,255,0.04); border-radius: 10px 10px 0 0; }
.tp-week:last-of-type { border-radius: 0 0 10px 10px; }
.tp-week__header {
  display: flex; justify-content: space-between; align-items: center;
  padding: 13px 22px; cursor: pointer; transition: background 0.15s;
}
.tp-week__header:hover { background: rgba(255,255,255,0.02); }
.tp-week__left { display: flex; align-items: center; gap: 12px; }
.tp-week__num {
  font-weight: 800; font-size: 13px; color: #fff;
  min-width: 36px;
  padding: 3px 8px; border-radius: 6px;
  background: rgba(255,255,255,0.06);
  text-align: center;
}
.tp-week__theme { color: #94a3b8; font-size: 13px; }
.tp-week__diff {
  font-size: 11px; color: #ffca28; font-weight: 600;
  padding: 2px 8px; border-radius: 6px;
  background: rgba(255,202,40,0.08);
}
.tp-week__arrow {
  font-size: 12px; color: #475569; transition: transform 0.2s;
}
.tp-week__arrow.open { transform: rotate(180deg); }
.tp-week__body { padding: 0 22px 14px; }
.tp-week__empty { color: #475569; font-size: 13px; padding: 10px 0; }

/* 题目行 */
.tp-problem {
  display: flex; align-items: center; gap: 10px;
  padding: 10px 14px; border-radius: 10px;
  background: rgba(255,255,255,0.02);
  border: 1px solid rgba(255,255,255,0.03);
  transition: all 0.15s; margin-bottom: 4px;
}
.tp-problem:hover {
  background: rgba(255,255,255,0.05);
  border-color: rgba(59,130,246,0.25);
}
.tp-problem--solved {
  background: rgba(52,211,153,0.04);
  border-color: rgba(52,211,153,0.15);
}
.tp-problem--attempted:not(.tp-problem--solved) {
  background: rgba(251,191,36,0.03);
  border-color: rgba(251,191,36,0.12);
}

/* 勾选框 */
.tp-problem__check {
  position: relative; width: 20px; height: 20px; flex-shrink: 0;
}
.tp-problem__check input {
  position: absolute; opacity: 0; cursor: pointer; height: 0; width: 0;
}
.tp-problem__check label {
  position: absolute; top: 0; left: 0;
  width: 20px; height: 20px;
  background: rgba(255,255,255,0.08);
  border: 1.5px solid rgba(255,255,255,0.2);
  border-radius: 5px; cursor: pointer;
  transition: all 0.15s ease;
}
.tp-problem__check label:hover {
  background: rgba(255,255,255,0.14);
  border-color: rgba(255,255,255,0.35);
}
.tp-problem__check input:checked + label {
  background: #34d399;
  border-color: #34d399;
}
.tp-problem__check input:checked + label:after {
  content: "";
  position: absolute; display: block;
  left: 6px; top: 2px;
  width: 6px; height: 11px;
  border: solid white; border-width: 0 2px 2px 0;
  transform: rotate(45deg);
}

.tp-problem__main {
  display: flex; align-items: center; gap: 10px; flex: 1;
  text-decoration: none; color: #e2e8f0;
  overflow: hidden; min-width: 0;
}
.tp-problem__diff {
  font-size: 11px; font-weight: 800; color: #ffca28;
  min-width: 30px; text-align: center; flex-shrink: 0;
}
.tp-problem__title {
  flex: 1; font-size: 13px;
  overflow: hidden; text-overflow: ellipsis; white-space: nowrap;
}
.tp-problem__tags { display: flex; gap: 4px; flex-shrink: 0; }
.tp-problem__tag {
  font-size: 10px; padding: 2px 8px; border-radius: 8px;
  background: rgba(59,130,246,0.08); color: #93c5fd;
}

/* 状态标签 */
.tp-problem__status {
  font-size: 11px; font-weight: 600; padding: 2px 8px;
  border-radius: 8px; flex-shrink: 0; white-space: nowrap;
}
.tp-status--none { color: #475569; background: rgba(255,255,255,0.03); }
.tp-status--solved { color: #34d399; background: rgba(52,211,153,0.1); }
.tp-status--attempted { color: #fbbf24; background: rgba(251,191,36,0.1); }

/* 操作栏 */
.tp-result .tp-top-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}
.tp-top-bar .tp-back { margin-bottom: 0; }

/* 知识点显隐切换 */
.tp-toggle-tags {
  padding: 6px 16px; border-radius: 10px;
  border: 1px solid rgba(255,255,255,0.12);
  background: rgba(255,255,255,0.04);
  color: #94a3b8; font-size: 13px; font-weight: 600;
  cursor: pointer; transition: all 0.15s ease;
}
.tp-toggle-tags:hover {
  background: rgba(255,255,255,0.08);
  border-color: rgba(255,255,255,0.22);
}
.tp-toggle-tags.active {
  background: rgba(99,102,241,0.15);
  border-color: rgba(99,102,241,0.4);
  color: #c7d2fe;
}

.tp-result__actions {
  display: flex; gap: 12px; margin-top: 32px; align-items: center;
}
.tp-saved-badge {
  color: #34d399; font-weight: 700; font-size: 14px;
  padding: 10px 20px; border-radius: 12px;
  background: rgba(52,211,153,0.08); border: 1px solid rgba(52,211,153,0.25);
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(8px); }
  to { opacity: 1; transform: translateY(0); }
}

@media (max-width: 640px) {
  .tp-header, .tp-saved, .tp-wizard, .tp-result { padding-left: 16px; padding-right: 16px; }
  .tp-overview__top { flex-direction: column; align-items: stretch; }
  .tp-overview__stats { flex-wrap: wrap; }
  .tp-stat { flex: 1 1 calc(50% - 10px); }
  .tp-levels, .tp-comps { grid-template-columns: 1fr 1fr; }
  .tp-plans-grid { grid-template-columns: 1fr; }
  .tp-header { padding-top: 16px; }
}
</style>
