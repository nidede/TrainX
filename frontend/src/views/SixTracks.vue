<template>
  <div class="tracks-page">
    <header class="tracks-header">
      <div>
        <div class="tracks-title">六大赛道</div>
        <p class="tracks-desc">从 ICPC、CCPC 到蓝桥杯、百度之星，展示每个比赛的赛制特点、备赛建议和核心训练场景。</p>
      </div>
      <router-link to="/home" class="tracks-back">返回首页</router-link>
    </header>

    <section class="tracks-grid">
      <router-link
        v-for="contest in contests"
        :key="contest.id"
        :to="`/contests/${contest.id}`"
        class="track-card"
      >
        <h3>{{ contest.name }}</h3>
        <p>{{ getIntro(contest.description) }}</p>
        <div class="track-meta">
          <span>主办：{{ contest.organizer }}</span>
          <span>频次：{{ contest.frequency }}</span>
        </div>
      </router-link>
      <div v-if="!loading && contests.length === 0" class="empty-state">
        当前没有可展示的比赛数据，请先运行后端数据脚本。
      </div>
      <div v-if="error" class="error-message">{{ error }}</div>
    </section>

    <footer class="tracks-footer">
    </footer>
  </div>
</template>

<script setup>
const contests = [
  {
    id: 'icpc',
    name: 'ICPC 国际大学生程序设计竞赛',
    organizer: 'ICPC Foundation',
    frequency: '每年举办',
    description: '全球最具影响力的大学生团队编程竞赛，强调高难题解与协同配合。',
    intro: '国际大学生程序设计竞赛，是面向高校队伍的综合挑战，考验算法能力与团队协作。'
  },
  {
    id: 'ccpc',
    name: 'CCPC 中国大学生程序设计竞赛',
    organizer: '中国计算机学会',
    frequency: '每年举办',
    description: '国内顶级大学生算法竞赛之一，题目风格兼顾算法与实现。',
    intro: 'CCPC 注重编程训练与工程化表达，是校园算法能力提升的重要赛道。'
  },
  {
    id: 'lanqiao',
    name: '蓝桥杯全国软件和信息技术专业人才大赛',
    organizer: '工业和信息化部人才交流中心',
    frequency: '每年举办',
    description: '兼顾软件开发、系统设计和项目实践，连接竞赛与企业岗位能力。',
    intro: '蓝桥杯是面向软件和信息技术人才的综合赛道，强调实践与技术实现能力。'
  },
  {
    id: 'baidu',
    name: '百度之星程序设计大赛',
    organizer: '百度',
    frequency: '每年举办',
    description: '聚焦智能算法与创新应用，适合希望进入大厂技术方向的选手。',
    intro: '百度之星以创新算法为核心，常见题型与搜索、推荐、图算法等前沿领域相关。'
  },
  {
    id: 'ruikang',
    name: '睿抗杯算法竞赛',
    organizer: '睿抗科技',
    frequency: '不定期',
    description: '面向算法工程与机器学习优化的专题竞赛，适合AI方向训练。',
    intro: '睿抗杯注重实战能力和算法优化，适合希望深入AI与优化题的学生。'
  },
  {
    id: 'matiji',
    name: '码蹄杯算法竞赛',
    organizer: '码蹄科技',
    frequency: '不定期',
    description: '以基础算法题和数据结构挑战为主，适合夯实程序设计基础。',
    intro: '码蹄杯聚焦基础题型，适合算法新手和打磨编程能力的训练阶段。'
  }
]

const getIntro = (intro) => intro || ''
</script>

<style scoped>
.tracks-page {
  min-height: 100vh;
  padding: 36px 0;
  color: #f8fafc;
  background: radial-gradient(circle at top left, rgba(255, 202, 40, 0.16), transparent 30%),
    radial-gradient(circle at right, rgba(41, 98, 255, 0.18), transparent 25%),
    linear-gradient(180deg, #060812 0%, #09111e 100%);
  font-family: "Consolas", "Monaco", monospace;
}
.tracks-header,
.tracks-grid,
.tracks-footer {
  max-width: 1400px;
  margin-left: auto;
  margin-right: auto;
  padding-left: 48px;
  padding-right: 48px;
}

.tracks-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 20px;
  padding: 24px 28px;
  margin-bottom: 32px;
  border-radius: 24px;
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(255, 255, 255, 0.08);
}

.tracks-title {
  font-size: 36px;
  font-weight: 800;
  margin-bottom: 10px;
}

.tracks-desc {
  margin: 0;
  color: #cbd5e1;
  max-width: 620px;
  line-height: 1.8;
}

.tracks-back {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 140px;
  padding: 12px 20px;
  border-radius: 16px;
  background: rgba(255, 255, 255, 0.08);
  color: #f8fafc;
  text-decoration: none;
  border: 1px solid rgba(255, 255, 255, 0.12);
}

.tracks-back:hover {
  background: rgba(255, 255, 255, 0.14);
}

.tracks-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 18px;
}

.track-card {
  min-height: 170px;
  padding: 24px;
  border-radius: 24px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.08);
  color: inherit;
  text-decoration: none;
  transition: transform 0.2s ease, background 0.2s ease;
}

.track-card:hover {
  transform: translateY(-4px);
  background: rgba(255, 255, 255, 0.12);
}

.track-card h3 {
  margin-top: 0;
  font-size: 22px;
  margin-bottom: 14px;
}

.track-card p {
  margin: 0 0 18px;
  color: #cbd5e1;
  line-height: 1.75;
}

.track-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  color: #94a3b8;
  font-size: 13px;
}

.empty-state,
.error-message {
  grid-column: 1 / -1;
  padding: 20px;
  border-radius: 20px;
  background: rgba(255, 255, 255, 0.06);
  color: #ffcc00;
}

.tracks-footer {
  margin-top: 32px;
  padding: 24px;
  border-radius: 24px;
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(255, 255, 255, 0.08);
  color: #cbd5e1;
}

@media (max-width: 980px) {
  .tracks-grid {
    grid-template-columns: 1fr;
  }

  .tracks-header {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>
