from django.contrib import admin
from .models import Quiz, Question, MultipleChoice, QuizResult, QuestionAnswer

admin.site.register(Quiz)
admin.site.register(Question)
admin.site.register(MultipleChoice)
admin.site.register(QuizResult)
admin.site.register(QuestionAnswer)
