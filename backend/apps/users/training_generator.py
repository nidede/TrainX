"""
训练计划生成算法

根据用户当前水平、目标赛事和目标奖项，生成个性化训练计划。
"""

import random
from apps.problems.models import Problem


# ── 赛事配置 ──────────────────────────────────────────────────
COMPETITION_CONFIGS = {
    'icpc': {
        'name': 'ICPC',
        'full_name': '国际大学生程序设计竞赛',
        'awards': ['区域赛铜牌', '区域赛银牌', '区域赛金牌', '世界总决赛'],
        'award_config': {
            '区域赛铜牌': {
                'target_difficulty': 3,
                'min_difficulty': 1,
                'key_tags': ['动态规划', '图论', '数据结构', '贪心', '深度优先搜索'],
                'week_multiplier': 1.0,
            },
            '区域赛银牌': {
                'target_difficulty': 4,
                'min_difficulty': 2,
                'key_tags': ['动态规划', '图论', '数据结构', '贪心', '数学', '数论'],
                'week_multiplier': 1.2,
            },
            '区域赛金牌': {
                'target_difficulty': 5,
                'min_difficulty': 3,
                'key_tags': ['动态规划', '图论', '数据结构', '数学', '数论', '计算几何', '网络流'],
                'week_multiplier': 1.5,
            },
            '世界总决赛': {
                'target_difficulty': 6,
                'min_difficulty': 4,
                'key_tags': ['动态规划', '图论', '数学', '数论', '计算几何', '网络流', '组合数学'],
                'week_multiplier': 2.0,
            },
        },
    },
    'ccpc': {
        'name': 'CCPC',
        'full_name': '中国大学生程序设计竞赛',
        'awards': ['省赛铜牌', '省赛银牌', '省赛金牌', '分站赛铜牌', '分站赛银牌', '分站赛金牌', '总决赛'],
        'award_config': {
            '省赛铜牌': {
                'target_difficulty': 2,
                'min_difficulty': 1,
                'key_tags': ['模拟', '贪心', '排序', '二分', '深度优先搜索'],
                'week_multiplier': 0.8,
            },
            '省赛银牌': {
                'target_difficulty': 3,
                'min_difficulty': 1,
                'key_tags': ['动态规划', '图论', '数据结构', '贪心', '深度优先搜索'],
                'week_multiplier': 1.0,
            },
            '省赛金牌': {
                'target_difficulty': 3,
                'min_difficulty': 2,
                'key_tags': ['动态规划', '图论', '数据结构', '贪心', '数学'],
                'week_multiplier': 1.2,
            },
            '分站赛铜牌': {
                'target_difficulty': 3,
                'min_difficulty': 2,
                'key_tags': ['动态规划', '图论', '数据结构', '贪心', '深度优先搜索'],
                'week_multiplier': 1.0,
            },
            '分站赛银牌': {
                'target_difficulty': 4,
                'min_difficulty': 2,
                'key_tags': ['动态规划', '图论', '数据结构', '贪心', '数学', '数论'],
                'week_multiplier': 1.3,
            },
            '分站赛金牌': {
                'target_difficulty': 5,
                'min_difficulty': 3,
                'key_tags': ['动态规划', '图论', '数据结构', '数学', '数论', '计算几何'],
                'week_multiplier': 1.5,
            },
            '总决赛': {
                'target_difficulty': 5,
                'min_difficulty': 4,
                'key_tags': ['动态规划', '图论', '数学', '数论', '计算几何', '网络流'],
                'week_multiplier': 1.8,
            },
        },
    },
    'lanqiao': {
        'name': '蓝桥杯',
        'full_name': '蓝桥杯全国软件和信息技术专业人才大赛',
        'awards': ['省赛三等奖', '省赛二等奖', '省赛一等奖', '国赛三等奖', '国赛二等奖', '国赛一等奖'],
        'award_config': {
            '省赛三等奖': {
                'target_difficulty': 1,
                'min_difficulty': 0,
                'key_tags': ['模拟', '排序', '暴力', '二分'],
                'week_multiplier': 0.6,
            },
            '省赛二等奖': {
                'target_difficulty': 2,
                'min_difficulty': 0,
                'key_tags': ['模拟', '排序', '暴力', '深度优先搜索', '二分'],
                'week_multiplier': 0.8,
            },
            '省赛一等奖': {
                'target_difficulty': 3,
                'min_difficulty': 1,
                'key_tags': ['动态规划', '深度优先搜索', '贪心', '二分', '数据结构'],
                'week_multiplier': 1.0,
            },
            '国赛三等奖': {
                'target_difficulty': 3,
                'min_difficulty': 1,
                'key_tags': ['动态规划', '深度优先搜索', '贪心', '数据结构', '图论'],
                'week_multiplier': 1.0,
            },
            '国赛二等奖': {
                'target_difficulty': 4,
                'min_difficulty': 2,
                'key_tags': ['动态规划', '图论', '数据结构', '贪心', '数学'],
                'week_multiplier': 1.3,
            },
            '国赛一等奖': {
                'target_difficulty': 4,
                'min_difficulty': 2,
                'key_tags': ['动态规划', '图论', '数据结构', '数学', '数论', '贪心'],
                'week_multiplier': 1.5,
            },
        },
    },
    'baidu': {
        'name': '百度之星',
        'full_name': '百度之星程序设计大赛',
        'awards': ['初赛晋级', '半决赛', '决赛铜牌', '决赛银牌', '决赛金牌'],
        'award_config': {
            '初赛晋级': {
                'target_difficulty': 2,
                'min_difficulty': 1,
                'key_tags': ['贪心', '模拟', '排序', '二分', '深度优先搜索'],
                'week_multiplier': 0.8,
            },
            '半决赛': {
                'target_difficulty': 3,
                'min_difficulty': 2,
                'key_tags': ['动态规划', '图论', '数据结构', '贪心', '数学'],
                'week_multiplier': 1.0,
            },
            '决赛铜牌': {
                'target_difficulty': 4,
                'min_difficulty': 2,
                'key_tags': ['动态规划', '图论', '数据结构', '贪心', '数学', '数论'],
                'week_multiplier': 1.2,
            },
            '决赛银牌': {
                'target_difficulty': 4,
                'min_difficulty': 3,
                'key_tags': ['动态规划', '图论', '数据结构', '数学', '数论', '计算几何'],
                'week_multiplier': 1.5,
            },
            '决赛金牌': {
                'target_difficulty': 5,
                'min_difficulty': 3,
                'key_tags': ['动态规划', '图论', '数学', '数论', '计算几何', '网络流'],
                'week_multiplier': 1.8,
            },
        },
    },
    'ruikang': {
        'name': '睿康杯',
        'full_name': '睿康杯大学生程序设计竞赛',
        'awards': ['铜牌', '银牌', '金牌'],
        'award_config': {
            '铜牌': {
                'target_difficulty': 2,
                'min_difficulty': 1,
                'key_tags': ['模拟', '贪心', '排序', '暴力', '深度优先搜索'],
                'week_multiplier': 0.8,
            },
            '银牌': {
                'target_difficulty': 3,
                'min_difficulty': 2,
                'key_tags': ['动态规划', '图论', '数据结构', '贪心', '数学'],
                'week_multiplier': 1.0,
            },
            '金牌': {
                'target_difficulty': 4,
                'min_difficulty': 2,
                'key_tags': ['动态规划', '图论', '数据结构', '数学', '贪心', '数论'],
                'week_multiplier': 1.3,
            },
        },
    },
    'matiji': {
        'name': '马蹄集',
        'full_name': '马蹄集算法竞赛',
        'awards': ['入门组', '提高组', '精英组'],
        'award_config': {
            '入门组': {
                'target_difficulty': 2,
                'min_difficulty': 0,
                'key_tags': ['模拟', '排序', '暴力', '贪心', '二分'],
                'week_multiplier': 0.7,
            },
            '提高组': {
                'target_difficulty': 3,
                'min_difficulty': 1,
                'key_tags': ['动态规划', '图论', '数据结构', '贪心', '深度优先搜索'],
                'week_multiplier': 1.0,
            },
            '精英组': {
                'target_difficulty': 4,
                'min_difficulty': 2,
                'key_tags': ['动态规划', '图论', '数据结构', '数学', '数论'],
                'week_multiplier': 1.3,
            },
        },
    },
}

# 水平描述
LEVEL_DESCRIPTIONS = {
    0: '零基础，尚未系统学习算法',
    1: '了解基础语法，能写简单程序',
    2: '掌握基础算法（排序、搜索、贪心）',
    3: '中等水平，熟悉DP和图论基础',
    4: '较高水平，掌握高级数据结构和高级DP',
    5: '竞赛水平，综合能力较强',
    6: '顶尖水平，能处理最难题目',
}

# 训练阶段模板
PHASE_TEMPLATES = {
    'foundation': {
        'name': '基础巩固',
        'description': '夯实基础，建立算法思维',
    },
    'core': {
        'name': '核心突破',
        'description': '针对赛事重点知识点强化训练',
    },
    'sprint': {
        'name': '冲刺模拟',
        'description': '综合练习与模拟赛',
    },
}


def calculate_duration_weeks(current_level, target_difficulty, week_multiplier):
    """根据水平差距计算训练周数"""
    gap = target_difficulty - current_level
    if gap <= 0:
        base_weeks = 3
    elif gap == 1:
        base_weeks = 6
    elif gap == 2:
        base_weeks = 10
    elif gap == 3:
        base_weeks = 14
    else:
        base_weeks = 18
    return max(3, round(base_weeks * week_multiplier))


def calculate_problems_per_week(current_level, target_difficulty):
    """根据水平差距计算每周推荐题量"""
    gap = target_difficulty - current_level
    if gap <= 0:
        return 5
    elif gap == 1:
        return 7
    elif gap == 2:
        return 8
    else:
        return 10


def select_problems_for_week(difficulty_range, focus_tags, count, used_ids, user_solved_ids=None):
    """从题库中选择适合某周的题目"""
    if user_solved_ids is None:
        user_solved_ids = set()

    min_d, max_d = difficulty_range

    # 优先选择知识点匹配的题目
    queryset = Problem.objects.filter(
        unified_difficulty__gte=min_d,
        unified_difficulty__lte=max_d,
    ).exclude(id__in=used_ids)

    tagged = queryset.filter(tags__name__in=focus_tags).distinct()
    untagged = queryset.exclude(tags__name__in=focus_tags).distinct()

    # 优先未做过的题
    tagged_unsolved = tagged.exclude(id__in=user_solved_ids)
    untagged_unsolved = untagged.exclude(id__in=user_solved_ids)

    selected_ids = []
    for qs in [tagged_unsolved, tagged, untagged_unsolved, untagged]:
        ids = list(qs.values_list('id', flat=True))
        random.shuffle(ids)
        for pid in ids:
            if pid not in selected_ids:
                selected_ids.append(pid)
            if len(selected_ids) >= count:
                break
        if len(selected_ids) >= count:
            break

    return selected_ids[:count]


def generate_training_plan(user, current_level, competition_key, award_name):
    """
    生成个性化训练计划

    返回 dict: {
        'duration_weeks': int,
        'problems_per_week': int,
        'phases': [...],
        'summary': str,
    }
    """
    comp = COMPETITION_CONFIGS.get(competition_key)
    if not comp:
        return None

    award = comp['award_config'].get(award_name)
    if not award:
        return None

    target_difficulty = award['target_difficulty']
    min_difficulty = award['min_difficulty']
    key_tags = award['key_tags']
    week_multiplier = award['week_multiplier']

    duration_weeks = calculate_duration_weeks(current_level, target_difficulty, week_multiplier)
    problems_per_week = calculate_problems_per_week(current_level, target_difficulty)

    # 获取用户已做题
    from apps.users.models import UserProblem
    user_solved_ids = set(
        UserProblem.objects.filter(user=user, solved=True).values_list('problem_id', flat=True)
    )

    # 划分训练阶段
    if duration_weeks <= 4:
        phases_config = [
            ('foundation', 0.3),
            ('core', 0.7),
        ]
    elif duration_weeks <= 8:
        phases_config = [
            ('foundation', 0.25),
            ('core', 0.5),
            ('sprint', 0.25),
        ]
    else:
        phases_config = [
            ('foundation', 0.2),
            ('core', 0.55),
            ('sprint', 0.25),
        ]

    phases = []
    used_ids = set()
    week_counter = 1

    for phase_key, ratio in phases_config:
        phase_weeks = max(1, round(duration_weeks * ratio))
        template = PHASE_TEMPLATES[phase_key]
        phase = {
            'key': phase_key,
            'name': template['name'],
            'description': template['description'],
            'weeks': [],
        }

        for i in range(phase_weeks):
            # 确定本周难度范围和重点
            if phase_key == 'foundation':
                # 基础阶段：从当前水平到 min_difficulty 的过渡
                start_d = current_level
                end_d = max(current_level, min_difficulty)
                # 逐步提升难度
                progress = i / max(phase_weeks, 1)
                week_min = start_d
                week_max = start_d + round((end_d - start_d + 1) * (progress + 1 / phase_weeks))
                week_max = min(week_max, end_d + 1)
                # 基础阶段多练基础知识点
                week_tags = ['模拟', '排序', '暴力', '贪心', '二分', '深度优先搜索']
            elif phase_key == 'core':
                # 核心阶段：围绕赛事重点知识点
                week_min = min_difficulty
                week_max = target_difficulty
                week_tags = key_tags
            else:
                # 冲刺阶段：综合难度，接近目标难度
                week_min = max(min_difficulty, target_difficulty - 1)
                week_max = target_difficulty + 1
                week_tags = key_tags

            # 确保难度范围有效
            week_min = max(0, week_min)
            week_max = max(week_min, week_max)

            # 选择本周主题（从重点知识点中轮流）
            tag_idx = i % len(week_tags)
            week_theme_tags = week_tags[tag_idx:tag_idx + 2]
            if len(week_theme_tags) < 2 and len(week_tags) > 1:
                week_theme_tags = week_tags[:2]
            theme_name = '·'.join(week_theme_tags) if week_theme_tags else '综合练习'

            problem_ids = select_problems_for_week(
                difficulty_range=(week_min, week_max),
                focus_tags=week_theme_tags,
                count=problems_per_week,
                used_ids=used_ids,
                user_solved_ids=user_solved_ids,
            )
            used_ids.update(problem_ids)

            # 获取题目详情
            problems_qs = Problem.objects.filter(id__in=problem_ids)
            problems_data = []
            for p in problems_qs:
                problems_data.append({
                    'id': p.id,
                    'title': p.title,
                    'difficulty': p.unified_difficulty,
                    'tags': [t.name for t in p.tags.all()],
                    'source_url': p.source_url,
                })

            # 按难度排序
            problems_data.sort(key=lambda x: (x['difficulty'] or 0, x['title']))

            phase['weeks'].append({
                'week': week_counter,
                'theme': theme_name,
                'difficulty_range': [week_min, week_max],
                'problems': problems_data,
            })
            week_counter += 1

        phases.append(phase)

    summary = (
        f"基于你当前 Lv{current_level} 的水平，针对 {comp['name']} {award_name} 目标，"
        f"建议进行 {duration_weeks} 周训练，每周 {problems_per_week} 题。"
        f"重点攻克：{'、'.join(key_tags[:5])}。"
    )

    return {
        'duration_weeks': duration_weeks,
        'problems_per_week': problems_per_week,
        'phases': phases,
        'summary': summary,
        'current_level': current_level,
        'target_competition': comp['name'],
        'target_competition_full': comp['full_name'],
        'target_award': award_name,
        'target_difficulty': target_difficulty,
        'key_tags': key_tags,
    }
