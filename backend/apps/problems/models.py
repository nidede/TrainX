from django.db import models


class Tag(models.Model):
    name = models.CharField(max_length=64, unique=True, verbose_name='标签名称')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = '题目标签'
        verbose_name_plural = '题目标签'

    def __str__(self):
        return self.name


class Problem(models.Model):
    title = models.CharField(max_length=255, verbose_name='题目名称')
    description = models.TextField(blank=True, verbose_name='题目描述')
    unified_difficulty = models.IntegerField(null=True, blank=True, verbose_name='统一难度')
    source_url = models.URLField(unique=True, verbose_name='源链接')
    platform = models.CharField(max_length=64, blank=True, verbose_name='平台')
    contest_name = models.CharField(max_length=128, blank=True, verbose_name='所属比赛/赛道')
    tags = models.ManyToManyField(Tag, blank=True, related_name='problems', verbose_name='知识点')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = '算法题目'
        verbose_name_plural = '算法题目'
        ordering = ['-unified_difficulty', 'title']

    def __str__(self):
        return self.title
