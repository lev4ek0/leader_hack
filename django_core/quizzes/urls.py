from quizzes import views
from rest_framework.routers import DefaultRouter
from django.urls import path

router = DefaultRouter()
router.register("quizzes", views.QuizzViewSet)

urlpatterns = [
    path("answers/", views.AnswerAPIView.as_view()),
    path("questions/", views.QuestionListAPIView.as_view()),
]
urlpatterns += router.urls
