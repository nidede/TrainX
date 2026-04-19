from rest_framework import viewsets
from rest_framework.pagination import PageNumberPagination
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.db import models
from django.shortcuts import get_object_or_404
from .models import Problem, Tag
from .serializers import ProblemSerializer, TagSerializer
import requests as http_requests


class ProblemViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Problem.objects.all()
    serializer_class = ProblemSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        difficulty = self.request.query_params.get('difficulty')
        if difficulty:
            levels = [int(d) for d in difficulty.split(',') if d.strip().isdigit()]
            if levels:
                queryset = queryset.filter(unified_difficulty__in=levels)
        tags = self.request.query_params.get('tags')
        if tags:
            tag_names = [t.strip() for t in tags.split(',') if t.strip()]
            if tag_names:
                queryset = queryset.filter(tags__name__in=tag_names).distinct()
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                models.Q(title__icontains=search) | models.Q(tags__name__icontains=search)
            ).distinct()

        # 按用户做题状态筛选（需登录）
        status_filter = self.request.query_params.get('status')
        if status_filter and self.request.user.is_authenticated:
            from apps.users.models import UserProblem
            if status_filter == 'solved':
                solved_ids = UserProblem.objects.filter(
                    user=self.request.user, solved=True
                ).values_list('problem_id', flat=True)
                queryset = queryset.filter(id__in=solved_ids)
            elif status_filter == 'attempted':
                attempted_ids = UserProblem.objects.filter(
                    user=self.request.user, solved=False
                ).values_list('problem_id', flat=True)
                queryset = queryset.filter(id__in=attempted_ids)
            elif status_filter == 'unsolved':
                done_ids = UserProblem.objects.filter(
                    user=self.request.user
                ).values_list('problem_id', flat=True)
                queryset = queryset.exclude(id__in=done_ids)

        # 排序
        ordering = self.request.query_params.get('ordering')
        if ordering in ('difficulty', '-difficulty', 'title', '-title'):
            field_map = {
                'difficulty': 'unified_difficulty',
                '-difficulty': '-unified_difficulty',
                'title': 'title',
                '-title': '-title',
            }
            queryset = queryset.order_by(field_map[ordering])
        return queryset


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all().order_by('name')
    serializer_class = TagSerializer
    pagination_class = None  # 标签数量不多，不需要分页

    def get_queryset(self):
        queryset = super().get_queryset()
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(name__icontains=search)
        return queryset


# ── 豆包翻译题目 ──────────────────────────────────

DOUBAO_API = 'https://ark.cn-beijing.volces.com/api/v3/chat/completions'
DOUBAO_MODEL = 'doubao-seed-2-0-mini-260215'
DOUBAO_KEY = 'ark-6055c1f0-022b-426a-a0de-b9441deba953-62a6d'


class ProblemTranslateView(APIView):
    """抓取原题页面并用豆包翻译为中文"""
    permission_classes = [AllowAny]

    def get(self, request, pk):
        problem = get_object_or_404(Problem, pk=pk)

        # 如果数据库已有翻译，直接返回
        if problem.translated_description:
            return Response({'description': problem.translated_description, 'translated': False})

        if not problem.source_url:
            return Response({'description': '暂无题目描述', 'translated': False})

        # 抓取原题页面文本
        try:
            resp = http_requests.get(problem.source_url, timeout=15, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            })
            resp.raise_for_status()
            page_text = _extract_text_from_html(resp.text)
        except Exception as e:
            return Response({'description': f'无法获取原题内容：{e}', 'translated': False})

        if not page_text or len(page_text.strip()) < 20:
            return Response({'description': '原题页面内容为空或无法解析', 'translated': False})

        # 调用豆包翻译（带重试）
        translated = None
        last_error = None
        for attempt in range(3):
            try:
                translated = _translate_with_doubao(problem.title, page_text)
                break
            except Exception as e:
                last_error = e
                import time
                if attempt < 2:
                    time.sleep(2 * (attempt + 1))
        if translated is None:
            return Response({'description': f'翻译失败：{last_error}', 'translated': False})

        # 保存翻译到新字段，不影响原始 description
        problem.translated_description = translated
        problem.save(update_fields=['translated_description', 'updated_at'])

        return Response({'description': translated, 'translated': True})


def _extract_text_from_html(html):
    """提取 HTML 中的题目内容，尽可能保留结构"""
    import re
    # 去除 script/style
    html = re.sub(r'<script[^>]*>[\s\S]*?</script>', '', html, flags=re.IGNORECASE)
    html = re.sub(r'<style[^>]*>[\s\S]*?</style>', '', html, flags=re.IGNORECASE)

    # 提取 problem-statement 区域（Codeforces）
    m = re.search(r'<div[^>]*class=["\']problem-statement["\'][^>]*>([\s\S]*?)(?=<div[^>]*class=["\'](?:roundbox|footer))', html, flags=re.IGNORECASE)
    if m:
        html = m.group(1)

    # 保留关键结构标签，其余去除
    html = re.sub(r'<br\s*/?>', '\n', html, flags=re.IGNORECASE)
    html = re.sub(r'</?(p|div|section|article|header|li|tr|td|th)[^>]*>', '\n', html, flags=re.IGNORECASE)
    # 保留数学公式中的内容
    html = re.sub(
        r'<span[^>]*class=["\'][^"\']*math[^"\']*["\'][^>]*>([\s\S]*?)</span>',
        r'$\1$',
        html, flags=re.IGNORECASE,
    )
    html = re.sub(
        r'<math[^>]*>([\s\S]*?)</math>',
        r'$\1$',
        html, flags=re.IGNORECASE,
    )
    # 去除剩余 HTML 标签
    text = re.sub(r'<[^>]+>', '', html)
    # 清理 HTML 实体
    text = text.replace('&lt;', '<').replace('&gt;', '>').replace('&amp;', '&').replace('&nbsp;', ' ')
    # 清理多余空白
    text = re.sub(r'[ \t]+', ' ', text)
    text = re.sub(r'\n\s*\n', '\n\n', text)
    text = text.strip()
    # 截取前3000字符，避免超时
    return text[:3000]


def _translate_with_doubao(title, raw_text):
    """调用豆包模型翻译题目"""
    prompt = (
        '你是一个专业的算法竞赛题目翻译专家。请将以下英文算法竞赛题目翻译为中文。\n\n'
        '要求：\n'
        '1. 使用 Markdown 格式输出\n'
        '2. 必须包含完整的题目描述、数据范围、输入格式、输出格式\n'
        '3. 必须包含所有样例（Sample Input / Sample Output），用代码块包裹\n'
        '4. 数学公式用 LaTeX 行内 $...$ 或块级 $...$ 格式\n'
        '5. 保持原文的所有细节，不要遗漏任何信息\n'
        '6. 用以下 Markdown 结构组织输出：\n\n'
        '## 题目描述\n（翻译内容）\n\n'
        '## 输入格式\n（翻译内容）\n\n'
        '## 输出格式\n（翻译内容）\n\n'
        '## 样例\n### 样例输入 1\n```\n（内容）\n```\n### 样例输出 1\n```\n（内容）\n```\n\n'
        '## 数据范围\n（翻译内容，包含所有变量范围约束）\n\n'
        '---\n\n'
        f'题目名称：{title}\n\n'
        f'原始内容：\n{raw_text}'
    )
    resp = http_requests.post(
        DOUBAO_API,
        headers={
            'Authorization': f'Bearer {DOUBAO_KEY}',
            'Content-Type': 'application/json',
        },
        json={
            'model': DOUBAO_MODEL,
            'messages': [{'role': 'user', 'content': prompt}],
        },
        timeout=120,
    )
    resp = http_requests.post(
        DOUBAO_API,
        headers={
            'Authorization': f'Bearer {DOUBAO_KEY}',
            'Content-Type': 'application/json',
        },
        json={
            'model': DOUBAO_MODEL,
            'messages': [{'role': 'user', 'content': prompt}],
        },
        timeout=60,
    )
    resp.raise_for_status()
    data = resp.json()
    return data['choices'][0]['message']['content']
