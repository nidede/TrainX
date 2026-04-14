from django.db import models

class Contest(models.Model):
    name = models.CharField(max_length=200, verbose_name='竞赛名称')
    description = models.TextField(verbose_name='竞赛介绍')
    website = models.URLField(verbose_name='官网链接')
    organizer = models.CharField(max_length=100, verbose_name='主办方')
    frequency = models.CharField(max_length=50, verbose_name='举办频率', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = '算法竞赛'
        verbose_name_plural = '算法竞赛'

    def __str__(self):
        return self.name
