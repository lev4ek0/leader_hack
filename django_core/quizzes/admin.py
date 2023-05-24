from django.contrib import admin

from quizzes import models


@admin.register(models.Quizz)
class QuizzAdmin(admin.ModelAdmin):
    pass


@admin.register(models.Question)
class QuestionAdmin(admin.ModelAdmin):
    pass


@admin.register(models.Option)
class OptionAdmin(admin.ModelAdmin):
    pass


@admin.register(models.QuizzCompletion)
class QuizzCompletiontAdmin(admin.ModelAdmin):
    pass
