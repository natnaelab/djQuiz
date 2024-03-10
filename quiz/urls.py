from django.urls import path
from .views import (
    HomeView,
    CreateQuizView,
    QuizDetailView,
    QuizDeleteView,
    AddQuestionView,
    EditQuizView,
    QuizResultsView,
    take_quiz,
    get_question,
    submit_answer,
)


app_name = "quiz"

urlpatterns = [
    path("", HomeView.as_view(), name="home"),
    path("create-quiz/", CreateQuizView.as_view(), name="create-quiz"),
    path("quiz/<str:slug>/", QuizDetailView.as_view(), name="quiz-detail"),
    path("quiz/<str:slug>/delete/", QuizDeleteView.as_view(), name="quiz-delete"),
    path("quiz/<str:slug>/edit/", EditQuizView.as_view(), name="edit-quiz"),
    path(
        "quiz/<str:slug>/add-question/", AddQuestionView.as_view(), name="add-question"
    ),
    path("quiz/<str:slug>/take-quiz/", take_quiz, name="take-quiz"),
    path("quiz/<str:slug>/question/", get_question, name="get-question"),
    path(
        "quiz/<str:slug>/submit-answer/<int:question_id>/",
        submit_answer,
        name="submit-answer",
    ),
    path("quiz/<str:slug>/results/", QuizResultsView.as_view(), name="quiz-results"),
]
