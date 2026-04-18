from rest_framework import serializers
from .models import Post, Comment, Category


class CategorySerializer(serializers.ModelSerializer):
    post_count = serializers.IntegerField(read_only=True, default=0)

    class Meta:
        model = Category
        fields = ('id', 'name', 'post_count', 'created_at')


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Comment
        fields = ('id', 'content', 'author', 'created_at')
        read_only_fields = ('author', 'created_at')


class PostListSerializer(serializers.ModelSerializer):
    author = serializers.StringRelatedField(read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True, default='')
    comment_count = serializers.IntegerField(read_only=True, default=0)

    class Meta:
        model = Post
        fields = (
            'id', 'title', 'summary', 'author', 'category', 'category_name',
            'is_published', 'view_count', 'comment_count',
            'created_at', 'updated_at',
        )


class PostDetailSerializer(serializers.ModelSerializer):
    author = serializers.StringRelatedField(read_only=True)
    author_id = serializers.IntegerField(source='author.id', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True, default='')
    comments = CommentSerializer(many=True, read_only=True)

    class Meta:
        model = Post
        fields = (
            'id', 'title', 'content', 'summary', 'author', 'author_id',
            'category', 'category_name', 'is_published',
            'view_count', 'comments', 'created_at', 'updated_at',
        )
        read_only_fields = ('author', 'view_count', 'created_at', 'updated_at')


class PostWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ('title', 'content', 'summary', 'category', 'is_published')
