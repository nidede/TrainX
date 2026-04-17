from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from .serializers import RegisterSerializer, UserSerializer, UserProblemSerializer, TrainingPlanSerializer
from .models import UserProblem, TrainingPlan
from .training_generator import generate_training_plan, COMPETITION_CONFIGS, LEVEL_DESCRIPTIONS


class RegisterView(APIView):
    authentication_classes = []   # 注册不需要认证，跳过 SessionAuthentication 的 CSRF 检查

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"msg": "注册成功"})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    authentication_classes = []   # 登录不需要认证，跳过 SessionAuthentication 的 CSRF 检查

    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")

        user = authenticate(username=username, password=password)

        if user:
            token, _ = Token.objects.get_or_create(user=user)
            return Response({"msg": "登录成功", "token": token.key})
        else:
            return Response({"msg": "用户名或密码错误"}, status=400)


class UserCenterView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        serializer = UserSerializer(user)
        return Response(serializer.data)


class UserProblemsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        user_problems = UserProblem.objects.filter(user=user).order_by('-updated_at')
        serializer = UserProblemSerializer(user_problems, many=True)
        return Response(serializer.data)

    def post(self, request):
        user = request.user
        problem_id = request.data.get('problem_id')
        solved = request.data.get('solved', False)

        try:
            user_problem, created = UserProblem.objects.get_or_create(
                user=user,
                problem_id=problem_id
            )
            user_problem.solved = solved
            if solved:
                from django.utils import timezone
                user_problem.solved_at = timezone.now()
            user_problem.save()
            return Response({"msg": "更新成功"})
        except Exception as e:
            return Response({"msg": "更新失败", "error": str(e)}, status=400)


class CompetitionConfigView(APIView):
    """返回赛事配置信息（水平描述、赛事列表、奖项列表）"""

    def get(self, request):
        data = {
            'levels': [
                {'value': k, 'description': v}
                for k, v in LEVEL_DESCRIPTIONS.items()
            ],
            'competitions': {
                key: {
                    'name': cfg['name'],
                    'full_name': cfg['full_name'],
                    'awards': cfg['awards'],
                }
                for key, cfg in COMPETITION_CONFIGS.items()
            },
        }
        return Response(data)


class GenerateTrainingPlanView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """生成训练计划预览（不持久化）"""
        current_level = request.data.get('current_level')
        competition_key = request.data.get('competition')
        award_name = request.data.get('award')

        if current_level is None or not competition_key or not award_name:
            return Response(
                {"msg": "请提供 current_level, competition, award"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            current_level = int(current_level)
        except (TypeError, ValueError):
            return Response({"msg": "current_level 必须是整数"}, status=400)

        if current_level < 0 or current_level > 6:
            return Response({"msg": "current_level 应在 0-6 之间"}, status=400)

        if competition_key not in COMPETITION_CONFIGS:
            return Response({"msg": "未知的赛事"}, status=400)

        comp = COMPETITION_CONFIGS[competition_key]
        if award_name not in comp['award_config']:
            return Response({"msg": "未知的奖项"}, status=400)

        plan_data = generate_training_plan(request.user, current_level, competition_key, award_name)
        if not plan_data:
            return Response({"msg": "生成计划失败"}, status=500)

        # 只返回预览数据，不保存到数据库
        return Response({
            'current_level': current_level,
            'target_competition': comp['name'],
            'target_award': award_name,
            'duration_weeks': plan_data['duration_weeks'],
            'problems_per_week': plan_data['problems_per_week'],
            'plan_data': plan_data,
        })


class SaveTrainingPlanView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """确认保存训练计划（持久化）"""
        current_level = request.data.get('current_level')
        competition_key = request.data.get('competition')
        award_name = request.data.get('award')

        if current_level is None or not competition_key or not award_name:
            return Response(
                {"msg": "请提供 current_level, competition, award"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            current_level = int(current_level)
        except (TypeError, ValueError):
            return Response({"msg": "current_level 必须是整数"}, status=400)

        if competition_key not in COMPETITION_CONFIGS:
            return Response({"msg": "未知的赛事"}, status=400)

        comp = COMPETITION_CONFIGS[competition_key]
        if award_name not in comp['award_config']:
            return Response({"msg": "未知的奖项"}, status=400)

        plan_data = generate_training_plan(request.user, current_level, competition_key, award_name)
        if not plan_data:
            return Response({"msg": "生成计划失败"}, status=500)

        plan = TrainingPlan.objects.create(
            user=request.user,
            current_level=current_level,
            target_competition=comp['name'],
            target_award=award_name,
            duration_weeks=plan_data['duration_weeks'],
            problems_per_week=plan_data['problems_per_week'],
            plan_data=plan_data,
        )

        serializer = TrainingPlanSerializer(plan)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class TrainingPlanListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        plans = TrainingPlan.objects.filter(user=request.user)
        serializer = TrainingPlanSerializer(plans, many=True)
        return Response(serializer.data)


class TrainingPlanDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        try:
            plan = TrainingPlan.objects.get(pk=pk, user=request.user)
        except TrainingPlan.DoesNotExist:
            return Response({"msg": "计划不存在"}, status=404)
        serializer = TrainingPlanSerializer(plan)
        return Response(serializer.data)

    def delete(self, request, pk):
        try:
            plan = TrainingPlan.objects.get(pk=pk, user=request.user)
        except TrainingPlan.DoesNotExist:
            return Response({"msg": "计划不存在"}, status=404)
        plan.delete()
        return Response({"msg": "已删除"})
