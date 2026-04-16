import json
import time
import requests
from requests.exceptions import RequestException

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from apps.problems.models import Problem, Tag


CODEFORCES_PROBLEMSET_API = 'https://codeforces.com/api/problemset.problems'


def _safe_request_json(url: str):
    try:
        resp = requests.get(url, timeout=20)
        resp.raise_for_status()
        return resp.json()
    except RequestException:
        raise


def _rating_to_level(rating):
    if rating is None:
        return 'unknown'
    try:
        rating = int(rating)
    except (TypeError, ValueError):
        return 'unknown'
    if rating < 1200:
        return 'easy'
    if rating < 1800:
        return 'medium'
    return 'hard'


def _rating_to_unified_difficulty(rating):
    if rating is None:
        return None
    try:
        rating = int(rating)
    except (TypeError, ValueError):
        return None
    if rating <= 800:
        return 0
    elif rating <= 1200:
        return 1
    elif rating <= 1600:
        return 2
    elif rating <= 2000:
        return 3
    elif rating <= 2400:
        return 4
    elif rating <= 2800:
        return 5
    else:
        return 6


# 英文标签到中文标签的映射字典
TAG_TRANSLATIONS = {
    'expression parsing': '表达式解析',
    'schedules': '调度',
    'ternary search': '三分查找',
    'flows': '网络流',
    'matrices': '矩阵',
    'string suffix structures': '字符串后缀结构',
    'two pointers': '双指针',
    'dsu': '并查集',
    'graph matchings': '图匹配',
    'strings': '字符串',
    'shortest paths': '最短路',
    '*special': '特殊问题',
    'hashing': '哈希',
    'communication': '通信',
    'geometry': '计算几何',
    'chinese remainder theorem': '中国剩余定理',
    'graphs': '图论',
    'combinatorics': '组合数学',
    'games': '博弈论',
    'bitmasks': '状态压缩',
    'number theory': '数论',
    'brute force': '暴力',
    'interactive': '交互题',
    'divide and conquer': '分治',
    'binary search': '二分',
    'trees': '树',
    'probabilities': '概率',
    'fft': '快速傅里叶变换',
    'dp': '动态规划',
    'dfs and similar': '深度优先搜索',
    'implementation': '模拟',
    'data structures': '数据结构',
    'math': '数学',
    'constructive algorithms': '构造算法',
    'sortings': '排序',
    'greedy': '贪心',
    'meet-in-the-middle': '折半搜索',
    '2-sat': '2-SAT'
}


def _get_or_create_tags(tag_names):
    tags = []
    for name in sorted(set(tag_names)):
        # 翻译标签名称
        translated_name = TAG_TRANSLATIONS.get(name.lower(), name)
        tag, _ = Tag.objects.get_or_create(name=translated_name)
        tags.append(tag)
    return tags


def _canonical_urls_for(contest_id, index):
    """Return canonical (problemset) and contest-style URLs for a problem."""
    if not contest_id:
        return None, None
    canonical = f'https://codeforces.com/problemset/problem/{contest_id}/{index}'
    contest = f'https://codeforces.com/contest/{contest_id}/problem/{index}'
    return canonical.rstrip('/'), contest.rstrip('/')


class Command(BaseCommand):
    help = 'Import Codeforces problem metadata via official API (不抓取题目描述)。'

    def add_arguments(self, parser):
        parser.add_argument('--limit', type=int, default=20, help='Number of problems to scrape.')
        parser.add_argument('--start', type=int, default=0, help='Offset in problem list.')

    def handle(self, *args, **options):
        limit = options['limit']
        start = options['start']

        self.stdout.write('Fetching Codeforces problem list via API...')
        try:
            payload = _safe_request_json(CODEFORCES_PROBLEMSET_API)
        except RequestException as exc:
            raise CommandError(f'请求 Codeforces API 失败：{exc}')

        if payload.get('status') != 'OK':
            raise CommandError('Codeforces API 返回非 OK 状态。')

        problems = payload['result']['problems'][start:start + limit]
        self.stdout.write(f'准备处理 {len(problems)} 个问题。')

        for item in problems:
            contest_id = item.get('contestId')
            index = item.get('index')
            title = item.get('name', '').strip()
            rating = item.get('rating')
            difficulty = _rating_to_level(rating)
            tags = item.get('tags', []) or []

            canonical_url, contest_url = _canonical_urls_for(contest_id, index)
            if not canonical_url:
                self.stdout.write(self.style.WARNING(f'跳过无 contestId 的题目：{title}'))
                continue

            platform = 'codeforces'
            contest_name = f'CF {contest_id}' if contest_id else ''
            description = '题目描述请访问原题链接。'

            unified_difficulty = _rating_to_unified_difficulty(rating)
            defaults = {
                'title': title,
                'unified_difficulty': unified_difficulty,
                'description': description,
                'platform': platform,
                'contest_name': contest_name,
            }

            # Candidate URLs to match existing records (cover common URL forms)
            candidates = [canonical_url]
            if contest_url:
                candidates.append(contest_url)
            # include trailing-slash variants
            candidates += [u + '/' for u in list(candidates)]

            with transaction.atomic():
                existing_qs = Problem.objects.filter(source_url__in=candidates)
                if existing_qs.exists():
                    # Prefer the record already using canonical url as primary
                    primary = existing_qs.filter(source_url=canonical_url).first() or existing_qs.first()
                    # Merge tags from duplicates
                    for other in existing_qs.exclude(pk=primary.pk):
                        for t in other.tags.all():
                            primary.tags.add(t)
                        other.delete()

                    # Update primary fields and ensure canonical URL
                    for k, v in defaults.items():
                        setattr(primary, k, v)
                    primary.source_url = canonical_url
                    primary.save()
                    if tags:
                        primary.tags.set(_get_or_create_tags(tags))
                    self.stdout.write(self.style.SUCCESS(f"合并并更新：{title} [{canonical_url}]"))
                else:
                    problem = Problem.objects.create(source_url=canonical_url, **defaults)
                    if tags:
                        problem.tags.set(_get_or_create_tags(tags))
                    self.stdout.write(self.style.SUCCESS(f"创建：{title} [{canonical_url}]"))

        self.stdout.write(self.style.SUCCESS('Codeforces 题目元数据导入完成。'))
