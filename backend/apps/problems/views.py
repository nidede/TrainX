from rest_framework import viewsets
from rest_framework.pagination import PageNumberPagination
from django.db import models
from .models import Problem, Tag
from .serializers import ProblemSerializer, TagSerializer


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
