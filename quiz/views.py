from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views import generic
from django.http import HttpResponse
from django.urls import reverse, reverse_lazy
from django.contrib import messages
from django.core.cache import cache
from .models import Quiz, QuizResult
from .forms import QuizForm, AddQuestionForm, MultipleChoiceFormSet, QuestionAnswerForm


class HomeView(generic.TemplateView):
    template_name = "home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["quizzes"] = Quiz.objects.filter(is_published=True).order_by(
            "-created_at"
        )
        return context


class CreateQuizView(LoginRequiredMixin, generic.CreateView):
    model = Quiz
    form_class = QuizForm
    template_name = "quiz/create_quiz.html"

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        form.save()
        messages.success(self.request, "Quiz created successfully")
        return redirect(
            reverse("quiz:quiz-detail", kwargs={"slug": form.instance.slug})
        )


class QuizDetailView(LoginRequiredMixin, generic.DetailView):
    model = Quiz
    template_name = "quiz/quiz_detail.html"


class QuizDeleteView(LoginRequiredMixin, UserPassesTestMixin, generic.DeleteView):
    model = Quiz
    success_url = reverse_lazy("quiz:home")
    success_message = "Quiz was Deleted successfully"

    def test_func(self):
        return self.get_object().created_by == self.request.user


class AddQuestionView(generic.View):
    def render_form_page_response(self, request, quiz, question_form, choice_formset):
        # render the form page with given context
        return render(
            request,
            template_name="quiz/add_question.html",
            context={
                "quiz": quiz,
                "question_form": question_form,
                "choice_formset": choice_formset,
            },
        )

    def get(self, request, slug):
        quiz = get_object_or_404(Quiz, slug=slug)
        question_form = AddQuestionForm()
        choice_formset = MultipleChoiceFormSet(prefix="choice")

        return self.render_form_page_response(
            request, quiz, question_form, choice_formset
        )

    def post(self, request, slug):
        quiz = get_object_or_404(Quiz, slug=slug)
        question_form = AddQuestionForm(request.POST)
        choice_formset = MultipleChoiceFormSet(prefix="choice")

        if question_form.is_valid():
            question = question_form.save(commit=False)
            question.quiz = quiz
            choice_formset = MultipleChoiceFormSet(request.POST, prefix="choice")

            if (
                question.question_type == "MULTIPLE_CHOICE"
                and choice_formset.is_valid()
            ):
                # save question with associated choices
                question.save()
                choices = choice_formset.save(commit=False)

                for choice in choices:
                    choice.question = question
                    choice.save()

                messages.success(request, "Question created successfully")
                return redirect(reverse("quiz:quiz-detail", kwargs={"slug": quiz.slug}))

            elif question.question_type == "SHORT_ANSWER":
                question.save()

                messages.success(request, "Question created successfully")
                return redirect(reverse("quiz:quiz-detail", kwargs={"slug": quiz.slug}))

        return self.render_form_page_response(
            request, quiz, question_form, choice_formset
        )


class EditQuizView(generic.UpdateView):
    model = Quiz
    form_class = QuizForm
    template_name = "quiz/edit_quiz.html"
    # success_url = reverse("my-quiz")

    def get_success_url(self) -> str:
        slug = self.kwargs.get("slug")
        return reverse("quiz:quiz-detail", kwargs={"slug": slug})


def get_question_form(question, user, post_data=None):
    instance = None
    try:
        instance = question.answers.get(user=user)
    except:
        pass

    return QuestionAnswerForm(question, post_data)


def take_quiz(request, slug):
    quiz = get_object_or_404(Quiz, slug=slug)
    QuizResult.objects.get_or_create(quiz=quiz, user=request.user)

    return render(request, "quiz/partials/take_quiz_content.html", {"quiz": quiz})


def get_question(request, slug):
    quiz = get_object_or_404(Quiz, slug=slug)
    questions = quiz.questions.all()
    question = questions.first()

    form = QuestionAnswerForm(question, session=request.session)
    question_number = list(questions).index(question) + 1

    return render(
        request,
        "quiz/partials/question.html",
        {"question": question, "form": form, "question_number": question_number},
    )


def submit_answer(request, slug, question_id):
    quiz = get_object_or_404(Quiz, slug=slug)
    question = get_object_or_404(quiz.questions, id=question_id)

    if request.method == "POST":
        form_action = request.POST.get("form_action", "").lower()

        if "back" in form_action:
            question = quiz.questions.filter(id__lt=question_id).last()
            form = QuestionAnswerForm(question, session=request.session)
        elif "skip" in form_action:
            question = quiz.questions.filter(id__gt=question_id).first()
            form = QuestionAnswerForm(question, session=request.session)
        elif "continue" in form_action:
            form = QuestionAnswerForm(
                question, session=request.session, data=request.POST
            )
            if form.is_valid():
                form.cache_answer(request.session)
                question = quiz.questions.filter(id__gt=question_id).first()
        elif "finish" in form_action:
            form = QuestionAnswerForm(
                question, session=request.session, data=request.POST
            )
            form.save_answer(request.user)
            for key in cache._cache.keys():
                if request.session.session_key in key:
                    cache.delete(key)

            response = HttpResponse()
            response["HX-Redirect"] = reverse(
                "quiz:quiz-results", kwargs={"slug": slug}
            )
            return response

    error = None
    if form.errors:
        error = form.non_field_errors()

    form = QuestionAnswerForm(question, session=request.session)
    return render(
        request,
        "quiz/partials/question.html",
        {"question": question, "form": form, "error": error},
    )


class QuizResultsView(generic.TemplateView):
    template_name = "quiz/quiz_results.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["quiz"] = Quiz.objects.get(slug=self.kwargs["slug"])
        return context
