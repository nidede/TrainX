from rest_framework.routers import DefaultRouter
from django.urls import path
from .views import ProblemViewSet, TagViewSet, ProblemTranslateView

router = DefaultRouter()
router.register(r'problems', ProblemViewSet)
router.register(r'tags', TagViewSet)

urlpatterns = router.urls + [
    path('problems/<int:pk>/translate/', ProblemTranslateView.as_view()),
]
