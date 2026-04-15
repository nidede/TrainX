from django.core.management.base import BaseCommand
from apps.crawler.models import Contest

class Command(BaseCommand):
    help = 'Scrape contest information from official websites'

    def handle(self, *args, **options):
        # ======================
        # 🔥 关键：先删除所有旧数据
        # ======================
        Contest.objects.all().delete()
        self.stdout.write(self.style.WARNING('已清空旧的竞赛信息'))

        contests_data = [
            {
                'name': 'ICPC 国际大学生程序设计竞赛',
                'website': 'https://icpc.global/',
                'organizer': 'ICPC Foundation',
                'description': 'ICPC 是全球范围内最具影响力的大学生程序设计竞赛之一。\n\n比赛采用团队形式，通常由三名队员协作解决 5-12 道高难度算法题，强调综合算法能力、数学推理和协同沟通。\n\n备赛建议：熟悉图论、动态规划、字符串、数论等核心算法题型，练习赛场时间管理，并培养队内分工与实时协作能力。',
                'frequency': '每年举办'
            },
            {
                'name': 'CCPC 中国大学生程序设计竞赛',
                'website': 'https://ccpc.io/',
                'organizer': '中国计算机学会',
                'description': 'CCPC 是中国高校最重要的程序设计比赛之一，旨在选拔优秀算法人才并推动大学算法教育发展。\n\n赛事分校内选拔、区域赛和全国总决赛，题目风格兼顾算法基础与工程实现，注重代码可靠性和效率。\n\n备赛建议：保持高频训练，熟练掌握数据结构、搜索、动态规划与贪心策略，同时积累工程型题目和竞赛实战经验。',
                'frequency': '每年举办'
            },
            {
                'name': '百度之星程序设计大赛',
                'website': 'https://astar.baidu.com/',
                'organizer': '百度',
                'description': '百度之星关注创新算法与技术应用，面向高校学生开放，是国内知名的企业级算法竞赛。\n\n竞赛题目常与人工智能、搜索排序、机器学习等前沿技术结合，强调创新解法与复杂问题分析。\n\n备赛建议：在常规算法训练外，补充图像处理、文本算法和大数据场景常见问题，并锻炼算法工程化表达能力。',
                'frequency': '每年举办'
            },
            {
                'name': '蓝桥杯全国软件和信息技术专业人才大赛',
                'website': 'https://www.lanqiao.cn/',
                'organizer': '工业和信息化部人才交流中心',
                'description': '蓝桥杯侧重软件开发能力与工程素养，是连接学术竞赛与企业实践的重要赛道。\n\n竞赛包含程序设计、软件测试、嵌入式系统等多个专业赛题，兼顾理论与实践，强调可维护性与项目实现能力。\n\n备赛建议：注重算法与工程融合，掌握常见开发框架、调试技巧与代码规范，同时积累项目实践案例。',
                'frequency': '每年举办'
            },
            {
                'name': '睿抗机器人开发者大赛 RAICOM',
                'website': 'https://www.raicom.com.cn/',
                'organizer': '工业和信息化部人才交流中心',
                'description': '睿抗机器人开发者大赛（RAICOM）是工信部人才交流中心主办的综合科创赛事。其中 CAIP 编程技能赛是最接近算法竞赛的个人赛项，采用 OI 赛制、高获奖率、时长较短、难度中等，定位介于蓝桥杯与 ACM 入门之间。\n\n参赛对象：中职、高职、本科、研究生；个人赛 1 人 1 机；分组包括研究生组、本科 A/B 组、高职高专组和中职组。\n\n赛制与流程：2 小时 5 题，采用 OI 赛制，实时可见分数，多次提交取最高，按测试点给分，支持部分得分，无罚时，语言支持 C/C++、Java、Python；评测环境为 OMS 系统。\n\n难度与考点：低于蓝桥杯国赛，接近蓝桥杯省赛；题目以模拟、暴力、基础数据结构、简单数学为主，常见高频考点包括字符串处理、枚举、贪心、输入输出、gcd/lcm、素数、快速幂、数组、栈、队列、哈希表、并查集、DFS/BFS、线性 DP、简单背包、简单最短路。\n\n含金量与价值：获奖率超高，省赛≥80%、国赛≈70%；工信部人才交流中心盖章证书，可作为保研/就业保底证书；适合新手稳奖、提升算法基础和竞赛经验。',
                'frequency': '每年举办'
            },
            {
                'name': '码蹄杯全国大学生程序设计大赛',
                'website': 'https://www.matiji.net/',
                'organizer': '全国高等学校计算机教育研究会',
                'description': '码蹄杯全国大学生程序设计大赛是全国高等学校计算机教育研究会主办的国家级算法竞赛，已列入全国普通高校大学生学科竞赛排行榜白名单。核心特点是 ACM 赛制、高获奖率、可多场刷分、直通百度之星，难度介于蓝桥杯与 ACM 区域赛之间。\n\n赛事采用个人 ACM 赛制，1 人 1 机，3 小时 10 题，按 AC 题数排名，题数相同则总用时优先，罚时本科组 20 分钟、职业/入门组 5 分钟。\n\n参赛对象包括本科、硕士、博士全日制在校生，社会人士可参与评奖；并设职业院校赛道和青少年挑战赛道。\n\n含金量：国家级白名单赛事、百度之星直通通道、全国高校普遍认可，适合冲奖、保研加分与就业保底。',
                'frequency': '每年举办'
            }
        ]

        # 重新插入
        for data in contests_data:
            contest = Contest.objects.create(**data)
            self.stdout.write(self.style.SUCCESS(f'已添加: {contest.name}'))

        self.stdout.write(self.style.SUCCESS('✅ 竞赛数据更新完成！'))