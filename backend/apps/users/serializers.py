from rest_framework import serializers
from .models import User, UserProblem, TrainingPlan, get_solved_problems_count, get_attempted_problems_count
from apps.problems.serializers import ProblemSerializer


class UserProblemSerializer(serializers.ModelSerializer):
    problem = ProblemSerializer(read_only=True)

    class Meta:
        model = UserProblem
        fields = ('id', 'problem', 'solved', 'solved_at', 'created_at', 'updated_at')


class UserSerializer(serializers.ModelSerializer):
    solved_problems_count = serializers.SerializerMethodField()
    attempted_problems_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'username', 'solved_problems_count', 'attempted_problems_count')

    def get_solved_problems_count(self, obj):
        return get_solved_problems_count(obj)

    def get_attempted_problems_count(self, obj):
        return get_attempted_problems_count(obj)


class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'password']

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password']
        )
        return user


class TrainingPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrainingPlan
        fields = (
            'id', 'current_level', 'target_competition', 'target_award',
            'duration_weeks', 'problems_per_week', 'plan_data', 'created_at',
        )
        read_only_fields = ('id', 'plan_data', 'created_at')