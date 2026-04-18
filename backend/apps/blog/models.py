from django.db import models
from django.conf import settings


class Category(models.Model):
    name = models.CharField(max_length=64, unique=True, verbose_name='分类名称')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = '博客分类'
        verbose_name_plural = '博客分类'
        ordering = ['name']

    def __str__(self):
        return self.name


class Post(models.Model):
    title = models.CharField(max_length=200, verbose_name='标题')
    content = models.TextField(verbose_name='正文（Markdown）')
    summary = models.CharField(max_length=300, blank=True, default='', verbose_name='摘要')
    is_published = models.BooleanField(default=True, verbose_name='是否发布')
    view_count = models.PositiveIntegerField(default=0, verbose_name='浏览量')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='blog_posts',
        verbose_name='作者',
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='posts',
        verbose_name='分类',
    )

    class Meta:
        verbose_name = '博客文章'
        verbose_name_plural = '博客文章'
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class Comment(models.Model):
    content = models.TextField(verbose_name='评论内容')
    created_at = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='blog_comments',
        verbose_name='评论者',
    )
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='文章',
    )

    class Meta:
        verbose_name = '评论'
        verbose_name_plural = '评论'
        ordering = ['created_at']

    def __str__(self):
        return f'{self.author} 评论了 {self.post}'
