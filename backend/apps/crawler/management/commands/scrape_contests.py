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
                'name': 'ICPC International Collegiate Programming Contest',
                'website': 'https://icpc.global/',
                'organizer': 'ICPC Foundation',
                'description': '国际大学生程序设计竞赛，是世界上最负盛名的大学生计算机竞赛之一。',
                'frequency': '每年举办'
            },
            {
                'name': 'CCPC中国大学生程序设计竞赛',
                'website': 'https://ccpc.io/',
                'organizer': '中国计算机学会',
                'description': '中国大学生程序设计竞赛，由中国计算机学会主办，是国内最高水平的大学生算法竞赛。',
                'frequency': '每年举办'
            },
            {
                'name': '百度之星程序设计大赛',
                'website': 'https://astar.baidu.com/',
                'organizer': '百度',
                'description': '百度之星程序设计大赛是由百度公司举办的面向全球大学生的算法竞赛。',
                'frequency': '每年举办'
            },
            {
                'name': '蓝桥杯全国软件和信息技术专业人才大赛',
                'website': 'https://www.lanqiao.cn/',
                'organizer': '工业和信息化部人才交流中心',
                'description': '蓝桥杯全国软件和信息技术专业人才大赛，是面向软件开发领域专业技术人才的全国性竞赛。',
                'frequency': '每年举办'
            },
            {
                'name': '睿抗杯算法竞赛',
                'website': 'https://www.ruikang.com/',
                'organizer': '睿抗科技',
                'description': '睿抗杯算法竞赛专注于人工智能和机器学习领域的算法挑战。',
                'frequency': '不定期'
            },
            {
                'name': '码蹄杯算法竞赛',
                'website': 'https://www.matiji.net/',
                'organizer': '码蹄科技',
                'description': '码蹄杯算法竞赛面向高校学生，提供算法编程和数据结构挑战。',
                'frequency': '不定期'
            }
        ]

        # 重新插入
        for data in contests_data:
            contest = Contest.objects.create(**data)
            self.stdout.write(self.style.SUCCESS(f'已添加: {contest.name}'))

        self.stdout.write(self.style.SUCCESS('✅ 竞赛数据更新完成！'))