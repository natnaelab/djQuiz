from django.test import TestCase, Client
from django.contrib.auth.models import User


class QuizTestCase(TestCase):
    def setUp(self):
        user = User.objects.create_user(username="testuser", password="secret")

        self.client.force_login(user)
