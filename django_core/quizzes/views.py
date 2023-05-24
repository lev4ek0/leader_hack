from rest_framework.viewsets import ModelViewSet

from quizzes.models import Quizz, Question
from quizzes.serializers import (
    QuizzDetailSerializer,
    QuizzListSerializer,
    AnswerSerializer,
    QuestionSerializer,
)
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Count


class QuizzViewSet(ModelViewSet):
    queryset = Quizz.objects.all()

    def get_queryset(self):
        return Quizz.objects.annotate(question_count=Count("questions"))

    def get_serializer_class(self):
        if self.action == "list":
            return QuizzListSerializer
        return QuizzDetailSerializer


class QuestionListAPIView(ListAPIView):
    serializer_class = QuestionSerializer
    queryset = Question.objects.all()
    filterset_fields = ("quizz", "order")


class AnswerAPIView(APIView):
    serializer_class = AnswerSerializer

    def post(self, request, *args, **kwargs):
        serializer = AnswerSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        resp_body = serializer.save()
        return Response(resp_body, status=status.HTTP_201_CREATED)
