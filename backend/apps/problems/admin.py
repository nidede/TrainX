from django.contrib import admin
from .models import Problem, Tag


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at', 'updated_at')
    search_fields = ('name',)


@admin.register(Problem)
class ProblemAdmin(admin.ModelAdmin):
    list_display = ('title', 'platform', 'unified_difficulty', 'source_url')
    search_fields = ('title', 'platform', 'contest_name')
    list_filter = ('platform', 'unified_difficulty')
    filter_horizontal = ('tags',)
