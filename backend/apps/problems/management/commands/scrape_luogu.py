import re
import time
import requests
from requests.exceptions import RequestException
from bs4 import BeautifulSoup

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from apps.problems.models import Problem, Tag


LUOGU_PROBLEM_URL = 'https://www.luogu.com.cn/problem/{pid}'
LUOGU_PROBLEMNEW_URL = 'https://www.luogu.com.cn/problemnew/show/{pid}'


def _get_or_create_tags(tag_names):
    tags = []
    for name in sorted(set([t for t in (tag_names or []) if t])):
        tag, _ = Tag.objects.get_or_create(name=name)
        tags.append(tag)
    return tags


def _normalize_pid(raw: str):
    if not raw:
        return None
    raw = raw.strip()
    # accept formats: P1000, 1000
    m = re.match(r'^[Pp]?(\d+)$', raw)
    if m:
        return m.group(1)
    return None


def _candidate_urls(pid: str):
    c1 = LUOGU_PROBLEM_URL.format(pid=pid).rstrip('/')
    c2 = LUOGU_PROBLEMNEW_URL.format(pid=pid).rstrip('/')
    candidates = [c1, c2, c1 + '/', c2 + '/']
    return candidates


def _fetch_problem_page(pid: str):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                      '(KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
        'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1'
    }
    for url in _candidate_urls(pid):
        try:
            resp = requests.get(url, headers=headers, timeout=10)
            if resp.status_code == 200 and resp.text:
                print(f"Successfully fetched page: {url}")
                # Print first 500 characters of the page to understand its structure
                print(f"Page preview: {resp.text[:500]}...")
                return url, BeautifulSoup(resp.text, 'html.parser')
            else:
                print(f"Failed to fetch page: {url}, status code: {resp.status_code}")
        except RequestException as e:
            print(f"Error fetching page: {e}")
            continue
    return None, None


def _parse_title(soup, pid: str):
    if not soup:
        return f'Luogu {pid}'
    # common fallbacks
    h1 = soup.find('h1')
    if h1 and h1.get_text(strip=True):
        return h1.get_text(strip=True)
    og = soup.find('meta', attrs={'property': 'og:title'})
    if og and og.get('content'):
        return og['content'].strip()
    title_tag = soup.find('title')
    if title_tag and title_tag.get_text(strip=True):
        return title_tag.get_text(strip=True)
    return f'Luogu {pid}'


def _parse_tags(soup):
    if not soup:
        return []
    # try meta keywords first
    meta = soup.find('meta', attrs={'name': 'keywords'})
    if meta and meta.get('content'):
        parts = [p.strip() for p in meta['content'].split(',') if p.strip()]
        return parts

    # find link-like tags
    found = []
    for a in soup.select('a'):
        href = a.get('href', '')
        if '/tag/' in href or '/topic/' in href:
            txt = a.get_text(strip=True)
            if txt:
                found.append(txt)
    return list(dict.fromkeys(found))


def _parse_difficulty(soup):
    if not soup:
        return ''
    
    # 尝试多种方法查找难度信息
    
    # 方法1：查找包含"难度"的所有元素
    for tag in soup.find_all(['span', 'div', 'p', 'li']):
        text = tag.get_text().strip()
        if '难度' in text:
            print(f"Found difficulty in {tag.name}: {text}")
            return text
    
    # 方法2：查找具有特定类名的元素
    difficulty_elements = soup.find_all(class_=lambda x: x and ('difficulty' in x.lower() or 'level' in x.lower()))
    for element in difficulty_elements:
        text = element.get_text().strip()
        if text:
            print(f"Found difficulty in class: {text}")
            return text
    
    # 方法3：查找可能包含难度信息的特定区域
    # 洛谷的难度信息通常在题目信息区域
    info_section = soup.find('div', class_=lambda x: x and ('info' in x.lower() or 'problem' in x.lower()))
    if info_section:
        for tag in info_section.find_all(['span', 'div']):
            text = tag.get_text().strip()
            if '难度' in text:
                print(f"Found difficulty in info section: {text}")
                return text
    
    # 方法4：查看页面中所有文本，寻找难度相关信息
    all_text = soup.get_text()
    if '难度' in all_text:
        # 提取包含难度的部分
        import re
        match = re.search(r'难度[^，。；；]+', all_text)
        if match:
            print(f"Found difficulty via regex: {match.group()}")
            return match.group()
    
    print("No difficulty found")
    # 打印页面的所有文本，以便分析页面结构
    print(f"Page text preview: {all_text[:1000]}...")
    return ''


def _luogu_difficulty_to_unified(difficulty):
    #  normalize difficulty string
    difficulty = difficulty.replace('难度：', '').replace('难度:', '').strip()
    print(f"Normalized difficulty: {difficulty}")
    
    # 映射规则，按照优先级从高到低处理
    if '入门' in difficulty:
        print(f"Mapping to level 0: {difficulty}")
        return 0
    elif '普及-' in difficulty:
        print(f"Mapping to level 1: {difficulty}")
        return 1
    elif '普及/提高-' in difficulty:
        print(f"Mapping to level 2: {difficulty}")
        return 2
    elif '普及+/提高' in difficulty:
        print(f"Mapping to level 3: {difficulty}")
        return 3
    elif '提高+/省选-' in difficulty:
        print(f"Mapping to level 4: {difficulty}")
        return 4
    elif '省选/NOI-' in difficulty:
        print(f"Mapping to level 5: {difficulty}")
        return 5
    elif 'NOI/NOI+/CTSC' in difficulty:
        print(f"Mapping to level 6: {difficulty}")
        return 6
    else:
        print(f"No mapping found for: {difficulty}")
        return None


class Command(BaseCommand):
    help = 'Scrape Luogu problems by PID(s) and import metadata into Problem model.'

    def add_arguments(self, parser):
        parser.add_argument('--pids', type=str, default='',
                            help='Comma-separated PIDs, e.g. P1000,1001 or 1000,1002')
        parser.add_argument('--start', type=int, default=0, help='Start numeric PID (inclusive)')
        parser.add_argument('--end', type=int, default=0, help='End numeric PID (inclusive)')
        parser.add_argument('--file', type=str, default='', help='Path to file with one PID per line')

    def handle(self, *args, **options):
        raw_pids = options.get('pids', '') or ''
        pids = []
        if raw_pids:
            for part in raw_pids.split(','):
                n = _normalize_pid(part)
                if n:
                    pids.append(n)

        start = options.get('start', 0) or 0
        end = options.get('end', 0) or 0
        if start and end and end >= start:
            pids += [str(i) for i in range(start, end + 1)]

        file_path = options.get('file', '')
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        n = _normalize_pid(line)
                        if n:
                            pids.append(n)
            except Exception as exc:
                raise CommandError(f'无法读取文件：{exc}')

        pids = [p for p in (pids or []) if p]
        if not pids:
            raise CommandError('未提供任何 PID。使用 --pids 或 --start/--end 或 --file 参数。')

        # deduplicate input list while preserving order
        seen = set()
        uniq_pids = []
        for pid in pids:
            if pid not in seen:
                seen.add(pid)
                uniq_pids.append(pid)

        self.stdout.write(f'准备处理 {len(uniq_pids)} 个 Luogu 题目')

        for pid in uniq_pids:
            self.stdout.write(f'处理 PID {pid} ...')
            try:
                url, soup = _fetch_problem_page(pid)
            except Exception as exc:
                self.stdout.write(self.style.WARNING(f'  获取页面失败：{exc}'))
                url, soup = None, None

            title = _parse_title(soup, pid)
            tags = _parse_tags(soup)
            difficulty = _parse_difficulty(soup)
            unified_difficulty = _luogu_difficulty_to_unified(difficulty)
            print(f"Final unified difficulty for {title}: {unified_difficulty}")
            # 不需要爬取题目描述，只保留基本信息
            description = '题目描述请访问原题链接。'

            canonical = LUOGU_PROBLEM_URL.format(pid=pid).rstrip('/')
            candidates = _candidate_urls(pid)

            defaults = {
                'title': title,
                'unified_difficulty': unified_difficulty,
                'description': description,
                'platform': 'luogu',
                'contest_name': '',
            }

            with transaction.atomic():
                existing_qs = Problem.objects.filter(source_url__in=candidates)
                if existing_qs.exists():
                    primary = existing_qs.filter(source_url=canonical).first() or existing_qs.first()
                    for other in existing_qs.exclude(pk=primary.pk):
                        for t in other.tags.all():
                            primary.tags.add(t)
                        other.delete()

                    for k, v in defaults.items():
                        setattr(primary, k, v)
                    primary.source_url = canonical
                    primary.save()
                    if tags:
                        primary.tags.set(_get_or_create_tags(tags))
                    self.stdout.write(self.style.SUCCESS(f'合并并更新：{title} [{canonical}]'))
                else:
                    problem = Problem.objects.create(source_url=canonical, **defaults)
                    if tags:
                        problem.tags.set(_get_or_create_tags(tags))
                    self.stdout.write(self.style.SUCCESS(f'创建：{title} [{canonical}]'))

            # be polite
            time.sleep(0.8)

        self.stdout.write(self.style.SUCCESS('Luogu 题目导入完成。'))
