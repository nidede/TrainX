from rest_framework import serializers
from .models import Problem, Tag


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name')


class ProblemSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)

    class Meta:
        model = Problem
        fields = (
            'id',
            'title',
            'description',
            'unified_difficulty',
            'platform',
            'contest_name',
            'source_url',
            'tags',
            'created_at',
            'updated_at',
        )
