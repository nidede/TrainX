from django.db import models
from django.contrib.auth.models import AbstractUser
from apps.problems.models import Problem

# Create your models here.

class User(AbstractUser):
    pass


class UserProblem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_problems')
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE, related_name='user_problems')
    solved = models.BooleanField(default=False)
    solved_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'problem')
        verbose_name = '用户题目记录'
        verbose_name_plural = '用户题目记录'

    def __str__(self):
        return f'{self.user.username} - {self.problem.title}'


class TrainingPlan(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='training_plans')
    current_level = models.IntegerField(verbose_name='当前水平')
    target_competition = models.CharField(max_length=100, verbose_name='目标赛事')
    target_award = models.CharField(max_length=100, verbose_name='目标奖项')
    duration_weeks = models.IntegerField(verbose_name='训练周数')
    problems_per_week = models.IntegerField(verbose_name='每周题量')
    plan_data = models.JSONField(default=dict, verbose_name='训练计划数据')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = '训练计划'
        verbose_name_plural = '训练计划'

    def __str__(self):
        return f'{self.user.username} - {self.target_competition} {self.target_award}'


# 扩展User模型，添加相关方法
def get_solved_problems_count(user):
    return UserProblem.objects.filter(user=user, solved=True).count()


def get_attempted_problems_count(user):
    return UserProblem.objects.filter(user=user).count()