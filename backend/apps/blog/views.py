from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.shortcuts import get_object_or_404

from .models import Post, Comment, Category
from .serializers import (
    PostListSerializer, PostDetailSerializer, PostWriteSerializer,
    CommentSerializer, CategorySerializer,
)


# ── 分类 ──────────────────────────────────────────

class CategoryListView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        categories = Category.objects.all()
        data = []
        for cat in categories:
            cat_data = CategorySerializer(cat).data
            cat_data['post_count'] = cat.posts.filter(is_published=True).count()
            data.append(cat_data)
        return Response(data)


# ── 文章列表 ──────────────────────────────────────

class PostListView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        queryset = Post.objects.filter(is_published=True)

        # 按分类筛选
        category_id = request.query_params.get('category')
        if category_id:
            queryset = queryset.filter(category_id=category_id)

        # 按关键词搜索
        search = request.query_params.get('search', '').strip()
        if search:
            queryset = queryset.filter(title__icontains=search)

        # 作者的文章（包含未发布的）
        author = request.query_params.get('author')
        if author:
            queryset = Post.objects.filter(author_id=author)
            if not (request.user.is_authenticated and str(request.user.id) == author):
                queryset = queryset.filter(is_published=True)

        # 分页
        page = int(request.query_params.get('page', 1))
        page_size = 10
        total = queryset.count()
        start = (page - 1) * page_size
        posts = queryset.select_related('author', 'category')[start:start + page_size]

        serializer = PostListSerializer(posts, many=True)
        for item in serializer.data:
            post_obj = next(p for p in posts if p.id == item['id'])
            item['comment_count'] = post_obj.comments.count()

        return Response({
            'results': serializer.data,
            'count': total,
            'page': page,
            'page_size': page_size,
        })

    def post(self, request):
        if not request.user.is_authenticated:
            return Response({'msg': '请先登录'}, status=status.HTTP_401_UNAUTHORIZED)
        serializer = PostWriteSerializer(data=request.data)
        if serializer.is_valid():
            post = serializer.save(author=request.user)
            return Response(PostDetailSerializer(post).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ── 文章详情 ──────────────────────────────────────

class PostDetailView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, pk):
        post = get_object_or_404(Post, pk=pk)
        if not post.is_published:
            if not request.user.is_authenticated or request.user != post.author:
                return Response({'msg': '文章不存在'}, status=status.HTTP_404_NOT_FOUND)
        # 浏览量 +1
        Post.objects.filter(pk=pk).update(view_count=post.view_count + 1)
        post.refresh_from_db()
        serializer = PostDetailSerializer(post)
        return Response(serializer.data)

    def put(self, request, pk):
        post = get_object_or_404(Post, pk=pk)
        if request.user != post.author:
            return Response({'msg': '无权编辑'}, status=status.HTTP_403_FORBIDDEN)
        serializer = PostWriteSerializer(post, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(PostDetailSerializer(post).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        post = get_object_or_404(Post, pk=pk)
        if request.user != post.author:
            return Response({'msg': '无权删除'}, status=status.HTTP_403_FORBIDDEN)
        post.delete()
        return Response({'msg': '删除成功'})


# ── 评论 ──────────────────────────────────────────

class CommentListView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, post_id):
        post = get_object_or_404(Post, pk=post_id)
        comments = post.comments.all()
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data)

    def post(self, request, post_id):
        if not request.user.is_authenticated:
            return Response({'msg': '请先登录'}, status=status.HTTP_401_UNAUTHORIZED)
        post = get_object_or_404(Post, pk=post_id)
        serializer = CommentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(author=request.user, post=post)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, post_id, pk=None):
        # 删除单条评论：DELETE /api/blog/posts/<post_id>/comments/<pk>/
        comment_id = request.query_params.get('id')
        if not comment_id:
            return Response({'msg': '缺少评论 ID'}, status=status.HTTP_400_BAD_REQUEST)
        comment = get_object_or_404(Comment, pk=comment_id, post_id=post_id)
        if request.user != comment.author:
            return Response({'msg': '无权删除'}, status=status.HTTP_403_FORBIDDEN)
        comment.delete()
        return Response({'msg': '删除成功'})


class CommentDeleteView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, post_id, pk):
        comment = get_object_or_404(Comment, pk=pk, post_id=post_id)
        if request.user != comment.author:
            return Response({'msg': '无权删除'}, status=status.HTTP_403_FORBIDDEN)
        comment.delete()
        return Response({'msg': '删除成功'})
