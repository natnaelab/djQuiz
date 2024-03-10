from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from .models import Quiz
from .views import add_question


class QuizCreationTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="secret")

    def test_create_quiz(self):
        self.client.login(username="testuser", password="secret")

        response_quiz = self.client.post(
            reverse("quiz:create-quiz"),
            {"title": "Test Quiz", "description": "This is a test quiz"},
        )

        self.assertEqual(response_quiz.status_code, 302)

        all_quizzes = Quiz.objects.all()
        self.assertEqual(all_quizzes.count(), 1)

        created_quiz = all_quizzes.first()

        def response_my_quiz(slug: str):
            return self.client.get(reverse("quiz:quiz-detail", kwargs={"slug": slug}))

        self.assertEqual(response_my_quiz(created_quiz.slug).status_code, 200)
        self.assertEqual(
            response_my_quiz(created_quiz.slug).resolver_match.view_name,
            "quiz:quiz-detail",
        )
        self.assertEqual(response_my_quiz("test").status_code, 404)

    def test_create_question_and_answer(self):
        quiz = Quiz.objects.create(title="Test Quiz", description="This is a test quiz")

        self.assertEqual(Quiz.objects.count(), 1)

        post_data = {
            "question_type": "MULTIPLE_CHOICE",
            "text": "What is the capital of Mexico?",
            "duration": 30,
            "explanation": "Mexico City is the capital of Mexico.",
            "choice-TOTAL_FORMS": 2,
            "choice-INITIAL_FORMS": 0,
            "choice-MIN_NUM_FORMS": 2,
            "choice-MAX_NUM_FORMS": 10,
            "choice-0-text": "London",
            "choice-0-is_correct": "False",
            "choice-1-text": "Mexico City",
            "choice-1-is_correct": "True",
        }

        response_add_q = self.client.post(
            reverse("quiz:add-question", kwargs={"slug": quiz.slug}), data=post_data
        )

        self.assertEqual(response_add_q.status_code, 302)
        questions = quiz.questions
        self.assertEqual(questions.count(), 1)
        self.assertEqual(questions.first().choices.count(), 2)
