from django.urls import path
from .views import HomeView, create_quiz, create_question_form

urlpatterns = [
    path("", HomeView.as_view(), name="home"),
    path("create-quiz/", create_quiz, name="create-quiz"),
    path("create-quiz/<str:slug>/", create_question_form, name="create-question-form"),
]
