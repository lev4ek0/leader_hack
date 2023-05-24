from rest_framework import serializers

from quizzes.models import Option, Question, Quizz, QuizzCompletion


class OptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Option
        fields = (
            "id",
            "text",
        )


class QuestionSerializer(serializers.ModelSerializer):
    options = OptionSerializer(many=True, read_only=True)

    class Meta:
        model = Question
        fields = (
            "id",
            "text",
            "image",
            "audio",
            "video",
            "options",
            "order",
            "is_multiple_choice",
        )


class QuizzListSerializer(serializers.ModelSerializer):
    question_count = serializers.IntegerField()

    class Meta:
        model = Quizz
        fields = ("id", "name", "question_count", "tags")


class QuizzDetailSerializer(QuizzListSerializer):
    pass


class AnswerSerializer(serializers.Serializer):
    question = serializers.PrimaryKeyRelatedField(queryset=Question.objects.all())
    options = serializers.PrimaryKeyRelatedField(
        queryset=Option.objects.all(), many=True
    )

    def create(self, validated_data):
        resp = validated_data["question"].check_answer(validated_data["options"])
        quizz = validated_data["question"].quizz
        quizz_completion, _ = QuizzCompletion.objects.get_or_create(
            quizz=quizz, user=self.context["request"].user
        )
        quizz_completion.latest_question = validated_data["question"]
        quizz_completion.save()
        return resp
