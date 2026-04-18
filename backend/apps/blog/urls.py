from django.urls import path
from .views import (
    CategoryListView,
    PostListView,
    PostDetailView,
    CommentListView,
    CommentDeleteView,
)

urlpatterns = [
    path('categories/', CategoryListView.as_view()),
    path('posts/', PostListView.as_view()),
    path('posts/<int:pk>/', PostDetailView.as_view()),
    path('posts/<int:post_id>/comments/', CommentListView.as_view()),
    path('posts/<int:post_id>/comments/<int:pk>/', CommentDeleteView.as_view()),
]
