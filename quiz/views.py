from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import TemplateView
from django.urls import reverse
from .models import Quiz
from .forms import QuizForm, QuestionForm
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator


class HomeView(TemplateView):
    template_name = "home.html"


def create_quiz(request):
    if request.method == "POST":
        form = QuizForm(request.POST)

        if form.is_valid():
            instance = form.save()
            return redirect(
                reverse("create-question-form", kwargs={"slug": instance.slug})
            )
    else:
        form = QuizForm()

    return render(request, "quiz/create-quiz.html", {"form": form})


def create_question_form(request, slug):
    if request.method == "POST":
        form = QuestionForm(request.POST)
    else:
        form = QuestionForm()

    quiz = get_object_or_404(Quiz, slug=slug)

    if quiz.published:
        return redirect(reverse("create-quiz"))

    context = {"quiz": quiz, "form": form}
    return render(request, "quiz/question-form.html", context)
