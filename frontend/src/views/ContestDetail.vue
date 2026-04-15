<template>
  <div class="detail-page">
    <header class="detail-header">
      <div>
        <div class="detail-title">{{ contest?.name || '加载中...' }}</div>
        <div class="detail-subtitle" v-if="contest">
          <span>{{ contest.organizer }} · {{ contest.frequency }}</span>
          <span v-if="contest.difficulty" class="difficulty-badge">难度：{{ contest.difficulty }}</span>
        </div>
      </div>
      <router-link to="/six-tracks" class="detail-back">返回赛道</router-link>
    </header>

    <section v-if="contest" class="detail-card">
      <div class="detail-summary">
        <p class="detail-lead">{{ contest.summary }}</p>
      </div>

      <div class="detail-meta">
        <div>
          <h3>官网链接</h3>
          <a :href="contest.website" target="_blank" rel="noreferrer">{{ contest.website }}</a>
        </div>
      </div>

      <div class="detail-section-card" v-for="section in contest.sections" :key="section.title">
        <h3>{{ section.title }}</h3>
        <ul>
          <li v-for="item in section.items" :key="item">{{ item }}</li>
        </ul>
      </div>
    </section>
    <section v-else class="detail-message error">
      未找到该比赛信息，请检查链接是否正确。
    </section>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  id: {
    type: String,
    required: true
  }
})

const contestData = {
  icpc: {
    name: 'ICPC 国际大学生程序设计竞赛',
    organizer: 'ICPC Foundation',
    frequency: '每年举办',
    difficulty: '★★★★★',
    website: 'https://icpc.global/',
    summary: 'ICPC 基于经典 ACM 赛制，是国际大学生程序设计竞赛的正式名称。3 人一组共享一台电脑，在 5 小时内解决多道高难度算法题，强调团队协作、算法建模与代码正确性。',
    sections: [
      {
        title: '历史沿革',
        items: [
          '创建历史：ICPC 的前身最早诞生于 1970 年，由美国德克萨斯 A&M 大学的计算机社团发起，最初只是一场美国德州本地的校际程序设计比赛，规模很小，仅限几所美国高校参与。',
          '现代意义上的 ICPC 正式成型于 1977 年，由 ACM（美国计算机学会）主办，因此长期被称为 ACM-ICPC。同年举办了第一届全球总决赛（World Finals），确立了核心规则：3 人一队、共用一台电脑、5 小时比赛、算法编程解题。',
          '早期比赛基本只在北美地区开展，由美国高校主导。',
          '发展历史：1980s–1990s 期间，比赛逐渐从美国扩展到欧洲、俄罗斯、亚太地区，建立起区域赛 → 总决赛的晋级体系，俄罗斯、波兰等东欧国家凭借强大的数学和算法基础迅速崛起。',
          '1996 年，ICPC 正式进入中国大陆，开始举办中国区区域赛，中国高校（上交、北大、清华等）快速成长，实力跻身世界前列。',
          '2002 年，上海交通大学拿下中国第一个 ICPC 世界冠军。',
          '成熟与商业化阶段（2000–2017）：IBM 长期赞助，比赛规模大幅扩大，成为全球最权威的大学生程序设计竞赛，中国成为 ICPC 全球最重要、参赛人数最多的赛区之一。',
          '机构改革阶段（2018 年至今）：ACM 退出主办，赛事由 ICPC Foundation（ICPC 基金会）独立运营，名称正式简化为 ICPC，但圈内仍习惯称为 “ACM 竞赛”；受疫情等影响赛制略有调整，但整体地位和含金量依旧是算法竞赛的顶峰。'
        ]
      },
      {
        title: 'ACM / ICPC 赛制说明',
        items: [
          '赛制类型：团队程序设计竞赛。',
          '组队：3 人一队，必须同校本科生。',
          '设备：全队共用 1 台电脑，同一时间只能一个人敲代码。',
          '时长：5 小时连续比赛。',
          '题目数量：通常 8～13 题。',
          '语言：主流 C/C++，部分赛区支持 Java、Python、Kotlin。'
        ]
      },
      {
        title: '比赛流程',
        items: [
          '开赛：发放题目（PDF/网页），开始计时。',
          '读题 & 讨论：三人分工读题、想思路、推样例。',
          '编码 & 调试：一人写代码，其他人辅助查错、分析边界。',
          '提交评测：把代码提交到在线判题系统（OJ）。',
          '实时反馈：系统立刻返回结果（AC/WA/TLE 等）。',
          '封榜：最后 60 分钟封榜，提交结果不再公开，排名隐藏。',
          '结束：按最终排名颁奖。'
        ]
      },
      {
        title: '判题结果',
        items: [
          'AC：答案正确，通过此题。',
          'WA：答案错误。',
          'TLE：运行超时。',
          'MLE：内存超限。',
          'RE：运行错误（数组越界、除零等）。',
          'PE：格式错误（空格、换行不对）。',
          'CE：编译失败。'
        ]
      },
      {
        title: '排名规则',
        items: [
          '排名按两个优先级严格比较：解题数量优先，总时间（含罚时）次之。',
          '每道 AC 题目，记录从比赛开始到 AC 的分钟数。',
          '每次错误提交（WA/TLE/RE 等）额外加 20 分钟罚时。',
          '未 AC 的题目不计罚时。',
          '总时间越小排名越靠前。'
        ]
      },
      {
        title: '传统特色',
        items: [
          '只能 3 人共用 1 台电脑，极度强调团队配合。',
          '罚时机制鼓励一次正确，不鼓励乱提交。',
          '封榜让最后 1 小时博弈感极强。',
          '只看算法与实现，不考工程、前端、后端、框架。',
          '难度极高，题目覆盖复杂数据结构、图论、数学、DP、字符串等。'
        ]
      },
      {
        title: '赛程环节',
        items: [
          '校内选拔：高校通常通过校赛选拔代表队，选拔结果决定区域赛参与资格。',
          '区域赛/省赛：区域赛是进入全球总决赛的关键环节，胜出队伍将获得晋级资格。',
          '邀请赛：在区域赛之外，部分高校和训练机构会组织邀请赛，模拟真实赛场节奏。',
          '全球总决赛：各区域冠军队伍参加，每年秋季举办，最终决出世界冠军。'
        ]
      },
      {
        title: '难度评估',
        items: [
          'ICPC 难度极高，对选手的算法深度、快速建模与状态维护要求都非常苛刻。',
          '对于国内高校队伍来说，达到区域赛水平通常需要扎实掌握 30+ 经典题型。'
        ]
      },
      {
        title: '备赛建议',
        items: [
          '重点训练图论、DP、字符串、数据结构和数学建模题型。',
          '进行团队模拟赛，练习分工、题目分配与时限管理。',
          '整理赛题笔记、复盘失误点，并持续提升代码调试能力。'
        ]
      }
    ]
  },
  ccpc: {
    name: 'CCPC 中国大学生程序设计竞赛',
    organizer: 'CCPC 组委会',
    frequency: '每年举办',
    difficulty: '★★★★☆',
    website: 'https://ccpc.io/',
    summary: 'CCPC 是国内本土最高级别、规模最大的团队算法编程竞赛，与 ICPC 同源但独立运营，含金量极高、认可度极强。',
    sections: [
      {
        title: '基本信息',
        items: [
          '全称：China Collegiate Programming Contest。',
          '创办：2015 年，首届在南阳理工学院举办。',
          '主办：CCPC 组委会（高校教练联盟），教育部计算机教指委支持。',
          '定位：国内顶级团队算法竞赛，被称为计算机竞赛“CBA”。',
          '核心宗旨：打破国际赛事垄断，建立中国自主高水平竞赛体系。'
        ]
      },
      {
        title: '参赛资格',
        items: [
          '组队：3 名在校本科生/专科生 + 1 名本校教练。',
          '年级限制：仅限本科生、专科生、研一学生，研二及以上不能参加。',
          '限制：每人每年最多参加 2 场分站赛（女生赛/高职赛不计）。'
        ]
      },
      {
        title: '完整赛制',
        items: [
          '比赛形式：5 小时连续比赛，3 人共用 1 台电脑，同一时间只能 1 人敲代码。',
          '题量：10～13 题，总决赛/分站赛通常 11～13 题。',
          '语言：C/C++（主流）、Java、Python、Kotlin。',
          '环境：标准 Linux 环境，gcc/g++、JDK、Python 等。'
        ]
      },
      {
        title: '比赛流程',
        items: [
          '发题 → 读题、讨论、想算法。',
          '编码 → 一人写代码，两人查错、想边界、算样例。',
          '提交 → 实时评测、立刻返回结果。',
          '气球机制：每 AC 一题发对应颜色气球，赛场可见。',
          '封榜：最后 60 分钟封榜，提交结果不公开、排名隐藏。',
          '结束 → 按最终排名颁奖。'
        ]
      },
      {
        title: '判题结果',
        items: [
          'AC：Accepted，通过。',
          'WA：Wrong Answer，答案错误。',
          'TLE：Time Limit Exceeded，超时。',
          'MLE：Memory Limit Exceeded，内存超限。',
          'RE：Runtime Error，运行错误（数组越界、除零等）。',
          'PE：Presentation Error，格式错误（空格/换行等）。',
          'CE：Compile Error，编译失败。'
        ]
      },
      {
        title: '排名规则',
        items: [
          '第一关键字：解题数量，做出题目越多排名越靠前。',
          '第二关键字：总时间（含罚时），每题用时 = 开赛到 AC 的分钟数。',
          '每次 WA/TLE/RE 额外加 20 分钟罚时，未 AC 不计罚时。',
          '总时间越小排名越高。'
        ]
      },
      {
        title: '完整赛季体系',
        items: [
          '校赛（3-4 月）：校内选拔，选出代表队。',
          '省赛（5-6 月）：各省独立举办，获取分站赛名额。',
          '网络预选赛（8 月底-9 月初）：全国统一线上赛，争夺分站赛正式名额。',
          '全国分站赛（9-11 月）：每年 4 场，约 260-280 支队伍，每场设金/银/铜奖，前若干名晋级总决赛。',
          '专项赛：CCPC 女生赛、高职专场，同样可晋级总决赛。',
          '全国总决赛（次年 3-4 月）：国内最高荣誉，约 130 支顶尖队伍参赛，决出全国冠亚季军、金奖。'
        ]
      },
      {
        title: 'CCPC 与 ICPC 区别',
        items: [
          '主办方：CCPC 组委会 / ICPC 基金会。',
          '创办：2015 年 / 1977 年。',
          '范围：中国大陆为主 / 全球。',
          '题面语言：分站/总决赛多为英文题面（少量中文），ICPC 全英文。',
          '参赛限制：最多 2 场分站赛 / 全球多区域可参加。',
          '难度：接近 ICPC 区域赛，略偏中国选手思维。'
        ]
      },
      {
        title: '含金量与价值',
        items: [
          '保研：985/211 计算机类保研加分极高，CCPC 金奖基本稳保研。',
          '就业：BAT、大厂、国企、银行 IT 等极度认可。',
          '能力：算法、逻辑、代码能力、团队协作全方位提升。',
          '人脉：结识全国顶尖选手与教练。'
        ]
      },
      {
        title: '难度与考点',
        items: [
          '难度极高，远高于蓝桥杯、天梯赛、PAT 等个人赛。',
          '核心考点：线段树、树状数组、平衡树、并查集、ST 表。',
          '图论：最短路、最小生成树、网络流、二分图、强连通分量。',
          '动态规划：线性 DP、区间 DP、状态压缩 DP、树形 DP、数位 DP。',
          '数学：数论、组合数学、博弈论、线性代数、计算几何。',
          '字符串：KMP、AC 自动机、后缀数组、Manacher、哈希。',
          '杂项：贪心、二分、枚举、模拟、高精度。'
        ]
      }
    ]
  },
  lanqiao: {
    name: '蓝桥杯全国大学生软件和信息技术大赛',
    organizer: '工业和信息化部人才交流中心',
    frequency: '每年举办',
    difficulty: '★★★☆☆',
    website: 'https://dasai.lanqiao.cn/',
    summary: '蓝桥杯是国内参与人数最多、覆盖最广、门槛适中的全国性 IT 学科竞赛，强调个人赛、OI 赛制、高获奖率和就业导向。',
    sections: [
      {
        title: '基本信息',
        items: [
          '全称：蓝桥杯全国大学生软件和信息技术大赛。',
          '主办：工业和信息化部人才交流中心（官方背景）。',
          '创办：2010 年，2025 年为第 16 届。',
          '定位：高校主流 IT 基础竞赛，具有就业/保研加分价值。',
          '规模：年参赛 20 万+，覆盖 1600+ 高校。',
          '核心宗旨：立足行业、突出实践、广泛参与、促进就业。'
        ]
      },
      {
        title: '参赛对象',
        items: [
          '身份：全日制研究生、本科生、高职高专生。',
          '形式：个人赛，一人一机。',
          '分组：研究生组、A 组（重点本科/985/211）、B 组（普通本科）、C 组（高职/专科）。'
        ]
      },
      {
        title: '赛项分类',
        items: [
          '软件类：C/C++ 程序设计、Java 软件开发、Python 程序设计、Web 应用开发、网络安全。',
          '电子类：单片机设计与开发、嵌入式设计与开发、物联网设计与开发、EDA/FPGA 设计。',
          '其他类别：项目实战赛（人工智能、智能体）、数字科技创新赛、视觉艺术设计赛、AIGC 专项赛。'
        ]
      },
      {
        title: '赛制与流程',
        items: [
          '赛程结构：两级赛制，包括省赛选拔赛和全国总决赛。',
          '赛程时间：报名 10 月-12 月，省赛 4 月，国赛 6 月。',
          '形式：个人单机离线编程，4 小时比赛。',
          '题量：填空 2 题 + 编程 6-8 题，共 8-10 题。',
          '环境：C/C++ 使用 Dev-C++，Java 使用 Eclipse，Python 使用 IDLE/Spyder。',
          '赛制关键：OI 赛制，无实时反馈，以最后一次提交为准，支持部分得分。'
        ]
      },
      {
        title: '判题与得分',
        items: [
          '填空题：完全正确得分，错误得 0 分。',
          '编程题：多组测试点，通过一个得一个分。',
          '无罚时：提交次数不影响分数。',
          '无封榜：全程不显示排名。',
          '特点：稳扎稳打、暴力骗分、部分得分策略非常有效。'
        ]
      },
      {
        title: '奖项与晋级',
        items: [
          '省赛：一、二、三等奖，比例约 10% / 15% / 25%，总获奖≤50%。',
          '晋级标准：省一等奖直接晋级国赛。',
          '全国总决赛：一、二、三等奖、优秀奖，比例约 10% / 25% / 40%，总获奖≤75%。',
          '证书：工信部人才交流中心盖章，权威性强。'
        ]
      },
      {
        title: '考点与难度',
        items: [
          '难度定位：远低于 ICPC/CCPC，适合入门与基础训练。',
          '高频考点：模拟、枚举、贪心、二分、排序、字符串处理。',
          '数学：数论（gcd/lcm、素数、快速幂）、组合、日期、几何。',
          '数据结构：数组、链表、栈、队列、树、图、并查集。',
          '动态规划：线性 DP、背包、区间 DP（简单）。',
          '图论：最短路（Floyd/Dijkstra）、最小生成树。',
          '搜索：DFS、BFS、回溯。'
        ]
      },
    ]
  },
  baidu: {
    name: '百度之星程序设计大赛',
    organizer: '百度在线网络技术（北京）有限公司',
    frequency: '每年举办',
    difficulty: '★★★★☆',
    website: 'https://astar.baidu.com/',
    summary: '百度之星是国内历史最久、影响力最强的企业级算法竞赛之一，采用 ACM 个人赛制，兼顾算法与工程化实现。',
    sections: [
      {
        title: '核心定位',
        items: [
          '主办方：百度在线网络技术（北京）有限公司。',
          '官网：astar.baidu.com，评测平台：matiji.net/astar。',
          '宗旨：以赛促学、以赛促研，为百度及互联网产业输送算法与工程人才。',
          '特色：个人赛制、ACM 赛规、高含金量校招通道、AI 与产业场景题融合。'
        ]
      },
      {
        title: '参赛资格',
        items: [
          '初赛：不限年龄、身份，校内学生与社会人士均可参加。',
          '总决赛：全日制在校学籍，专科、本科、研究生、中小学生均可报名（以初赛报名学籍为准）。',
          '社会人士仅可参与初赛/决赛“打星”，不占决赛名额、不参与排名。'
        ]
      },
      {
        title: '赛制与赛程',
        items: [
          '个人参赛：一人一机，独立完成。',
          '计分规则：总时间=解题时间总和+错误提交次数×20 分钟，与 ICPC/CCPC 一致。',
          '判题结果：AC/WA/TLE/MLE/RE/PE/CE，实时反馈。',
          '排名规则：解题数优先，总时间越短排名越高。'
        ]
      },
      {
        title: '常规赛程',
        items: [
          '初赛：通常在 6 月 29 日、8 月 10 日两场可选，3 小时，8 题，线上进行。',
          '总决赛：通常在 12 月 7 日举行，5 小时，11-12 题，线下赛场进行。',
          '初赛每场约 400 人晋级，两场共约 800 人入围总决赛，取最佳成绩。',
          '总决赛按绝对成绩排名，分组评奖。'
        ]
      },
      {
        title: '比赛环境与语言',
        items: [
          '支持语言：C/C++、Python、Java、Kotlin，以 C/C++ 为主。',
          '评测环境：标准 Linux 环境，gcc/g++、JDK、Python。',
          '与工业级环境一致，兼顾算法效率与工程实现。'
        ]
      },
      {
        title: '奖项设置',
        items: [
          '初赛：按绝对成绩设奖，不分省、不分组，金奖≈5%、银奖≈10%、铜奖≈15%。',
          '总决赛：大学组/高中组/小星星组，设总冠军、名次奖和专项奖。',
          '总决赛奖金：总冠军 20000 元、2-3 名 10000 元、4-6 名 8000 元、7-10 名 4000 元。',
          '荣誉：百度官方认证证书，优秀选手纳入百度人才库。'
        ]
      },
      {
        title: '考点与难度',
        items: [
          '难度接近 ICPC/CCPC 区域赛，高于蓝桥杯。',
          '题量 5 小时 11-12 题，对算法深度、代码效率和时间管理要求极高。',
        ]
      },
      {
        title: '含金量与价值',
        items: [
          '百度绿色通道：决赛选手可获百度校招/实习直通卡，优先面试、免笔试。',
          '企业认可度：字节、阿里、腾讯、华为等头部科技公司高度认可。',
          '人才库通道：优秀选手进入百度人才库，长期获得就业机会推荐。',
          '保研加分：多数 985/211 高校将其列为保研竞赛目录，国奖可获强加分。',
          '学术能力证明：竞赛成绩是研究生申请和科研项目选拔的重要参考。'
        ]
      },
      {
        title: '与其他主流竞赛对比',
        items: [
          '赛制：百度之星个人 ACM / ICPC 团队 ACM / 蓝桥杯 OI。',
          '参赛形式：个人赛 / 团队赛 / 个人赛。',
          '时长：初赛 3 小时、决赛 5 小时 / 5 小时 / 4 小时。',
          '难度：高（接近 ICPC 区域赛） / 极高（全球顶级） / 基础-中等。',
          '含金量：极高（就业/保研双优） / 顶级（国际认可） / 中高（就业/保研基础）。',
          '核心优势：百度校招通道、产业题融合 / 国际影响力、团队协作 / 入门友好、高获奖率。'
        ]
      }
    ]
  },
  ruikang: {
    name: '睿抗机器人开发者大赛 RAICOM',
    organizer: '工业和信息化部人才交流中心',
    frequency: '每年举办',
    difficulty: '★★★☆☆',
    website: 'https://www.raicom.com.cn/',
    summary: '睿抗 CAIP 编程技能赛是 2 小时、5 题、OI 赛制、超高获奖率的工信部个人算法赛，难度低于蓝桥杯，适合新手保底、保研/就业加分。',
    sections: [
      {
        title: '基本信息',
        items: [
          '全称：睿抗机器人开发者大赛（RAICOM）。',
          '主办：工业和信息化部人才交流中心。',
          '核心赛道：CAIP 信息技术创新赛道 → 编程技能赛。',
          '定位：入门友好、高获奖、工信部证书、适合保研/就业保底。'
        ]
      },
      {
        title: '参赛对象',
        items: [
          '身份：全日制中职、高职、本科、研究生。',
          '形式：个人赛，1 人 1 机。',
          '分组：研究生组、本科 A/B 组、高职高专组、中职组。'
        ]
      },
      {
        title: '赛制与流程',
        items: [
          '时长：2 小时，比蓝桥杯短一半。',
          '题量：5 题，省赛与国赛题目数量一致。',
          '赛制：OI 赛制，可见分数、多次提交取最高、按测试点累计得分。',
          '评测：即时反馈、无罚时、支持部分得分。',
          '语言：C/C++、Java、Python；评测系统：OMS。'
        ]
      },
      {
        title: '难度与考点',
        items: [
          '难度：低于蓝桥杯国赛，接近蓝桥杯省赛。',
          '风格：节奏快、重基础、轻高难算法。',
          '考点：模拟、暴力、字符串、枚举、贪心、输入输出。',
          '数学：gcd/lcm、素数、快速幂、日期、简单数论。',
          '数据结构：数组、栈、队列、哈希表、并查集。',
          '搜索与 DP：基础 DFS/BFS、线性 DP、简单背包。',
          '图论：简单最短路（Dijkstra/Floyd）。'
        ]
      },
      {
        title: '奖项与晋级',
        items: [
          '省赛获奖率≥80%，省一/省二可直接晋级国赛。',
          '国赛获奖率≈70%，竞赛证书由工信部人才交流中心盖章。',
          '适合稳奖、作为保研/就业保底证书和简历补充项。'
        ]
      },
      {
        title: '含金量与价值',
        items: [
          '工信部证书：官方权威背书。',
          '保研加分：多数高校国二/国三可加分，国一加分接近蓝桥杯国二。',
          '就业认可：国企、银行、中小厂认可度高，大厂认可度低于蓝桥杯和 ACM。',
          '优势：2 小时短赛、实时可见分、多次提交取最高、获奖率极高。'
        ]
      },
      {
        title: '与蓝桥杯/ACM 对比',
        items: [
          '赛制：睿抗 CAIP 为 OI（可见分+多次提交取最高），蓝桥杯为 OI（不可见分+最后一次提交），ACM 为罚时赛。',
          '时长：2 小时 / 4 小时 / 5 小时。',
          '题量：5 题 / 8-10 题 / 10-13 题。',
          '难度：低-中 / 中 / 极高。',
          '获奖率：省赛≈80% / 省赛≈50% / 区域赛≈30%。',
          '含金量：中 / 中高 / 顶级。'
        ]
      }
    ]
  },
  matiji: {
    name: '码蹄杯全国大学生程序设计大赛',
    organizer: '全国高等学校计算机教育研究会',
    frequency: '每年举办',
    difficulty: '★★★★☆',
    website: 'https://www.matiji.net/',
    summary: '码蹄杯是国家级白名单算法竞赛，采用 ACM 个人赛制、3 小时 10 题、高获奖率、可多场取最优，难度介于蓝桥杯与 ACM 区域赛之间。',
    sections: [
      {
        title: '基本信息',
        items: [
          '主办方：全国高等学校计算机教育研究会。',
          '赛事等级：国家级 A 类（白名单）。',
          '合作单位：百度公司，拥有百度之星直通机制。',
          '参赛平台：码蹄精选题库 OJ（matiji.net）。'
        ]
      },
      {
        title: '参赛对象',
        items: [
          '本科院校赛道：本科、硕士、博士全日制在校生，社会人士可参与评奖。',
          '职业院校赛道：高职、高专、中职、技师学院在校生。',
          '青少年挑战赛道：提高组与本科赛道同题同场，入门组难度更低。'
        ]
      },
      {
        title: '赛制与赛程',
        items: [
          '核心赛制：ACM 个人赛，1 人 1 机。',
          '时长：3 小时，题量：10 题（本科组/青少年提高组）。',
          '计分：按 AC 题数排名，题数相同时总用时少者靠前。',
          '罚时：本科组 20 分钟/次，职业组与入门组 5 分钟/次。',
          '实时榜单、即时评测、支持重测，语言：C/C++、Python、Java。'
        ]
      },
      {
        title: '赛程安排',
        items: [
          '报名：每年 1-5 月。',
          '初赛省赛：5-7 月，三场可选，取最优成绩，线上双机位监控。',
          '决赛国赛：9-10 月，线上/线下分年度安排。'
        ]
      },
      {
        title: '奖项与晋级',
        items: [
          '初赛省赛获奖率约 50%，金银铜奖比例约 1:2:2。',
          '晋级规则：金奖、银奖直接晋级国赛，约 30% 晋级率。',
          '国赛获奖率约 60%，设优秀奖和专项奖（如一血、最佳女选手、优秀教练）。'
        ]
      },
      {
        title: '难度与考点',
        items: [
          '本科组难度：接近蓝桥杯国赛，略低于 ACM 区域赛。',
          '职业/入门组难度：低于蓝桥杯省赛。',
          '高频考点：模拟、枚举、贪心、字符串、数学（gcd、快速幂）。',
          '数据结构：栈、队列、并查集、树状数组、线段树。',
          '图论：最短路、最小生成树、拓扑排序。',
          'DP 与搜索：线性 DP、背包、区间 DP、DFS、BFS、记忆化搜索。',
          '进阶：简单计算几何、数论、状态压缩。'
        ]
      },
      {
        title: '含金量与核心优势',
        items: [
          '国家级白名单赛事，全国高校普遍认可。',
          '国奖可获保研/综测强力加分。',
          '百度之星绿色通道：决赛获奖者推荐直通百度之星总决赛。',
          '获奖选手纳入百度人才库，优先获得校招/实习机会。',
          '三场初赛刷最优、3 小时短赛、获奖率高、容错率大。'
        ]
      },
      {
        title: '与蓝桥杯/ACM 对比',
        items: [
          '赛制：码蹄杯 ACM（罚时、实时榜）/ 蓝桥杯 OI（最后一次提交）/ ACM 团队（5 小时）。',
          '时长：3 小时 / 4 小时 / 5 小时。',
          '题量：10 题 / 8-10 题 / 10-13 题。',
          '参赛形式：个人 / 个人 / 3 人团队。',
          '获奖率：省赛50%/国赛60% / 蓝桥杯省赛50%/国赛20% / 区域赛≈30%。',
          '难度：中（蓝桥杯国赛水平）/ 中 / 极高。',
          '特色：多场刷分、直通百度 / 覆盖广、证书量大 / 国际顶级、含金量最高。'
        ]
      }
    ]
  }
}

const contest = computed(() => contestData[props.id])
</script>

<style scoped>
.detail-page {
  min-height: 100vh;
  padding: 36px 40px;
  color: #f8fafc;
  background: radial-gradient(circle at top left, rgba(255, 202, 40, 0.16), transparent 30%),
    radial-gradient(circle at right, rgba(41, 98, 255, 0.18), transparent 25%),
    linear-gradient(180deg, #060812 0%, #09111e 100%);
  font-family: "Consolas", "Monaco", monospace;
}

.detail-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 20px;
  padding: 24px 28px;
  margin-bottom: 32px;
  border-radius: 24px;
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(255, 255, 255, 0.08);
}

.detail-title {
  font-size: 36px;
  font-weight: 800;
  margin-bottom: 10px;
}

.detail-subtitle {
  margin: 0;
  color: #cbd5e1;
  line-height: 1.8;
}

.detail-back {
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

.detail-back:hover {
  background: rgba(255, 255, 255, 0.14);
}

.detail-message {
  padding: 24px;
  border-radius: 20px;
  background: rgba(255, 255, 255, 0.06);
  color: #cbd5e1;
}

.detail-message.error {
  color: #ffbaba;
}

.detail-card {
  padding: 28px;
  border-radius: 28px;
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(255, 255, 255, 0.1);
  box-shadow: 0 24px 80px rgba(0, 0, 0, 0.18);
}

.detail-meta {
  display: grid;
  gap: 18px;
  margin-bottom: 24px;
}

.detail-meta h3 {
  margin: 0 0 10px;
}

.detail-section-card {
  padding: 22px 24px;
  margin-bottom: 18px;
  border-radius: 24px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.detail-section-card h3 {
  margin-top: 0;
}

.detail-subtitle {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
  align-items: center;
}

.difficulty-badge {
  display: inline-flex;
  align-items: center;
  padding: 6px 12px;
  border-radius: 999px;
  background: rgba(255, 202, 40, 0.18);
  color: #ffd54f;
  font-size: 14px;
  border: 1px solid rgba(255, 202, 40, 0.35);
}

.detail-meta a {
  color: #8ab4f8;
  text-decoration: none;
}

.detail-meta a:hover {
  text-decoration: underline;
}

.detail-description {
  padding: 28px;
  border-radius: 24px;
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(255, 255, 255, 0.08);
}

.detail-description p {
  margin: 0 0 18px;
  color: #cbd5e1;
  line-height: 1.8;
}

@media (max-width: 980px) {
  .detail-header {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>
