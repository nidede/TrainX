from django.urls import path
from .views import (
    RegisterView, LoginView, UserCenterView, UserProblemsView,
    CompetitionConfigView, GenerateTrainingPlanView, SaveTrainingPlanView,
    TrainingPlanListView, TrainingPlanDetailView,
)

urlpatterns = [
    path('register/', RegisterView.as_view()),
    path('login/', LoginView.as_view()),
    path('center/', UserCenterView.as_view()),
    path('problems/', UserProblemsView.as_view()),
    path('competition-config/', CompetitionConfigView.as_view()),
    path('training-plans/', TrainingPlanListView.as_view()),
    path('training-plans/generate/', GenerateTrainingPlanView.as_view()),
    path('training-plans/save/', SaveTrainingPlanView.as_view()),
    path('training-plans/<int:pk>/', TrainingPlanDetailView.as_view()),
]