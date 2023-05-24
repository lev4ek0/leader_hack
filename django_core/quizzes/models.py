from typing import TYPE_CHECKING

from django.db import models
from django.contrib.postgres.fields import ArrayField

if TYPE_CHECKING:
    from authentication_app.models import User


class Quizz(models.Model):
    name = models.CharField(max_length=255, verbose_name="Название")

    tags = ArrayField(
        models.CharField(max_length=127),
        blank=True,
        null=True,
        verbose_name="Тэги",
    )

    def __str__(self) -> str:
        return self.name

    class Meta:
        verbose_name = "Викторина"
        verbose_name_plural = "Викторины"


class Question(models.Model):
    text = models.TextField(verbose_name="Текст", blank=True)

    image = models.ImageField(
        upload_to="quizzes/questions/images",
        blank=True,
        verbose_name="Изображение",
    )

    audio = models.FileField(
        upload_to="quizzes/questions/audios",
        blank=True,
        verbose_name="Аудио",
    )

    video = models.FileField(
        upload_to="quizzes/questions/videos",
        blank=True,
        verbose_name="Видео",
    )

    quizz: Quizz = models.ForeignKey(
        to=Quizz,
        on_delete=models.CASCADE,
        related_name="questions",
        verbose_name="Викторина",
    )

    correct_info = models.TextField(
        blank=True, verbose_name="Информация при правильном ответе"
    )

    incorrect_info = models.TextField(
        blank=True, verbose_name="Информация при неправильном ответе"
    )

    order = models.PositiveSmallIntegerField(verbose_name="Порядок")

    is_multiple_choice = models.BooleanField(
        default=False, verbose_name="Множественный выбор?"
    )

    def check_answer(self, answers: list["Option"]) -> bool:
        """
        Проверяет правильность ответа.
        """
        correct_answers = []
        incorrect_answers = []
        is_correct = False
        for answer in answers:
            if answer.question == self and answer.is_correct:
                correct_answers.append(answer.id)
            else:
                incorrect_answers.append(answer.id)
        if len(correct_answers) == self.options.filter(is_correct=True).count():
            is_correct = True
        resp = {
            "is_correct": is_correct,
            "correct_answers": correct_answers,
            "incorrect_answers": incorrect_answers,
        }
        if is_correct:
            resp["info"] = self.correct_info
        else:
            resp["info"] = self.incorrect_info
        return resp

    class Meta:
        verbose_name = "Вопрос"
        verbose_name_plural = "Вопросы"


class Option(models.Model):
    text = models.CharField(max_length=512, verbose_name="Текст", blank=True)

    question: Question = models.ForeignKey(
        to=Question,
        on_delete=models.CASCADE,
        related_name="options",
        verbose_name="Вопрос",
    )

    is_correct = models.BooleanField(default=False, verbose_name="Правильный?")

    class Meta:
        verbose_name = "Вариант ответа"
        verbose_name_plural = "Варианты ответа"


class QuizzCompletion(models.Model):
    quizz: Quizz = models.ForeignKey(
        to=Quizz,
        on_delete=models.CASCADE,
        related_name="completions",
        verbose_name="Викторина",
    )

    user: "User" = models.ForeignKey(
        to="authentication_app.User",
        on_delete=models.CASCADE,
        related_name="quizz_completions",
        verbose_name="Пользователь",
    )

    latest_question: Question = models.ForeignKey(
        to=Question,
        on_delete=models.CASCADE,
        related_name="latest_at_completions",
        verbose_name="Последний вопрос",
        null=True,
    )

    points_earned = models.PositiveSmallIntegerField(
        verbose_name="Количество набранных баллов",
        default=0,
    )

    class Meta:
        verbose_name = "Прохождение викторины"
        verbose_name_plural = "Прохождения викторин"
