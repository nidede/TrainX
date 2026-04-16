from rest_framework.routers import DefaultRouter
from .views import ProblemViewSet, TagViewSet

router = DefaultRouter()
router.register(r'problems', ProblemViewSet)
router.register(r'tags', TagViewSet)

urlpatterns = router.urls
