from django.db import models
from django.conf import settings
from django.utils.text import slugify
from .utils.unique_slugify import unique_slugify


class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Quiz(BaseModel):
    title = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    description = models.TextField()
    published = models.BooleanField(default=False)

    class Meta:
        verbose_name_plural = "Quizzes"

    def __str__(self) -> str:
        return self.title

    def save(self, *args, **kwargs) -> None:
        slug = slugify(self.title)
        self.slug = unique_slugify(self, slug)
        super(Quiz, self).save(*args, **kwargs)


class QuizResult(BaseModel):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    score = models.PositiveIntegerField()

    def __str__(self) -> str:
        return f"{self.user.username} - {self.quiz} - Score: {self.score}"


class Question(models.Model):
    QuestionType = models.TextChoices("QuestionType", "CHOICE SHORT_ANSWER")

    text = models.TextField()
    duration = models.PositiveIntegerField(default=60)
    correct_short_answer = models.CharField(max_length=50, blank=True, null=True)
    explanation = models.TextField(blank=True, null=True)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name="questions")
    question_type = models.CharField(
        max_length=15, choices=QuestionType.choices, default=QuestionType.CHOICE
    )

    def __str__(self) -> str:
        return self.text


class Choice(models.Model):
    text = models.CharField(max_length=100)
    question = models.ForeignKey(
        Question, on_delete=models.CASCADE, related_name="choices"
    )
    CORRECT_INCORRECT_CHOICES = ((True, "Correct"), (False, "Incorrect"))
    is_correct = models.BooleanField(choices=CORRECT_INCORRECT_CHOICES, default=False)

    def __str__(self) -> str:
        return self.text


class UserAnswer(BaseModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    selected_choice = models.ForeignKey(
        Choice, blank=True, null=True, on_delete=models.SET_NULL
    )
    time_spent = models.PositiveIntegerField()

    @property
    def time_expired(self):
        return (self.question.duration - self.time_spent) < 0

    def __str__(self) -> str:
        return f"{self.user.username} - {self.question} - {self.selected_choice}"
