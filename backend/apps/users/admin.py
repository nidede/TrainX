from django.contrib import admin
from .models import User, UserProblem, TrainingPlan

# Register your models here.

admin.site.register(User)
admin.site.register(UserProblem)
admin.site.register(TrainingPlan)