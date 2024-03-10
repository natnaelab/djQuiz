from django.db import models
from django.utils.text import slugify
from django.conf import settings
import string
from django.utils.crypto import get_random_string


def unique_slugify(instance, slug):
    model = instance.__class__
    unique_slug = slug
    while model.objects.filter(slug=unique_slug).exists() or unique_slug == "":
        allowed_chars = string.ascii_letters + string.digits + "_-"
        unique_slug = slug + get_random_string(length=6, allowed_chars=allowed_chars)

    return unique_slug


class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Quiz(BaseModel):
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, max_length=255)
    description = models.TextField(null=True, blank=True)
    is_published = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    is_timed = models.BooleanField(default=True)
    time_limit = models.PositiveIntegerField()

    class Meta:
        verbose_name_plural = "Quizzes"

    def __str__(self) -> str:
        return self.title

    # get quiz participants
    def get_participants(self):
        return self.results.all().values_list("user", flat=True)

    def save(self, *args, **kwargs) -> None:
        if self.pk is None:
            # set slug when first creating a quiz object
            slug = slugify(self.title, allow_unicode=True)
            self.slug = unique_slugify(self, slug)
        super(Quiz, self).save(*args, **kwargs)


class QuizResult(BaseModel):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name="results")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    answers = models.ManyToManyField("QuestionAnswer")

    def __str__(self) -> str:
        return f"{self.user.username} - {self.quiz}"


class Question(models.Model):
    text = models.TextField()
    duration = models.PositiveIntegerField(default=60)
    correct_short_answer = models.CharField(max_length=50, blank=True, null=True)
    explanation = models.TextField(blank=True, null=True)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name="questions")
    QuestionType = models.TextChoices("QuestionType", "MULTIPLE_CHOICE SHORT_ANSWER")
    question_type = models.CharField(
        max_length=15,
        choices=QuestionType.choices,
        default=QuestionType.MULTIPLE_CHOICE,
    )

    def get_question_number(self):
        return list(self.quiz.questions.order_by("id")).index(self) + 1

    def __str__(self) -> str:
        return self.text


class MultipleChoice(models.Model):
    text = models.CharField(max_length=100)
    question = models.ForeignKey(
        Question, on_delete=models.CASCADE, related_name="choices"
    )
    CORRECT_INCORRECT_CHOICES = ((True, "Correct"), (False, "Incorrect"))
    is_correct = models.BooleanField(choices=CORRECT_INCORRECT_CHOICES, default=False)

    def __str__(self) -> str:
        return self.text


class QuestionAnswer(BaseModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    question = models.ForeignKey(
        Question, on_delete=models.CASCADE, related_name="answers"
    )
    multiple_choice = models.ManyToManyField(MultipleChoice)
    short_answer = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self) -> str:
        return f"{self.user.username} - {self.question}"
