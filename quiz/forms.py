from typing import Any
from django import forms
from django.core.cache import cache
from .models import Quiz, Question, MultipleChoice, QuestionAnswer


class BaseStyledModelForm(forms.ModelForm):
    default_widget_attrs = {
        "class": "border bg-white px-4 py-2 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
    }

    def __init__(self, *args, **kwargs):
        super(BaseStyledModelForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            self.style_field(field_name)

    def style_field(self, field_name):
        field = self.fields.get(field_name)

        if field:
            field.widget.attrs.update(self.default_widget_attrs)


class QuizForm(BaseStyledModelForm):
    class Meta:
        model = Quiz
        fields = ("title", "description")
        widgets = {
            "title": forms.TextInput(attrs={"placeholder": "Enter Quiz Title"}),
            "description": forms.Textarea(attrs={"placeholder": "Enter description"}),
        }

    def __init__(self, *args, **kwargs) -> None:
        super(QuizForm, self).__init__(*args, **kwargs)
        description_field = self.fields.get("description")
        description_field.widget.attrs["class"] += " h-28"


class MultipleChoiceForm(BaseStyledModelForm):
    class Meta:
        model = MultipleChoice
        fields = ("text", "is_correct")
        widgets = {"text": forms.TextInput(attrs={"placeholder": "Enter choice"})}

    def __init__(self, *args, **kwargs) -> None:
        super(MultipleChoiceForm, self).__init__(*args, **kwargs)
        text_field = self.fields.get("text")
        text_field.widget.attrs["class"] += " w-full"

        correct_field = self.fields.get("is_correct")
        correct_field.widget.attrs["class"] += " flex-1"


class BaseFormSet(forms.BaseInlineFormSet):
    def clean(self):
        non_empty_texts_count = sum(
            1 for form in self.forms if form.cleaned_data.get("text")
        )
        correct_choices_count = sum(
            1 for form in self.forms if form.cleaned_data.get("is_correct")
        )

        if non_empty_texts_count < 2:
            raise forms.ValidationError(
                '"Multiple Choice" type questions must have at least 2 Choices'
            )

        if correct_choices_count < 1:
            raise forms.ValidationError("Question must have atleast one correct choice")


MultipleChoiceFormSet = forms.inlineformset_factory(
    Question,
    MultipleChoice,
    form=MultipleChoiceForm,
    formset=BaseFormSet,
    min_num=2,
    max_num=10,
    extra=1,
)


class AddQuestionForm(BaseStyledModelForm):
    class Meta:
        model = Question
        fields = (
            "question_type",
            "text",
            "duration",
            "correct_short_answer",
            "explanation",
        )
        widgets = {
            "text": forms.Textarea(attrs={"placeholder": "Enter question text"}),
            "correct_short_answer": forms.TextInput(
                attrs={"placeholder": "Enter answer"}
            ),
            "explanation": forms.Textarea(
                attrs={"placeholder": "Enter explanation for your answer"}
            ),
        }

    def __init__(self, *args, **kwargs) -> None:
        super(AddQuestionForm, self).__init__(*args, **kwargs)
        text_field = self.fields.get("text")
        text_field.widget.attrs["class"] += " h-14"

        correct_short_answer_field = self.fields.get("correct_short_answer")
        correct_short_answer_field.widget.attrs["class"] += " w-full"

        expalanation_field = self.fields.get("explanation")
        expalanation_field.widget.attrs["class"] += " h-20"

    def clean(self) -> dict[str, Any]:
        cleaned_data = super().clean()
        correct_short_answer = cleaned_data.get("correct_short_answer")

        if (
            cleaned_data.get("question_type") == "SHORT_ANSWER"
            and not correct_short_answer
        ):
            self.add_error("correct_short_answer", "Answer field cannot be empty")
            self.fields["correct_short_answer"].widget.attrs[
                "class"
            ] += " border-red-600 focus:ring-red-600"

        return cleaned_data


class QuestionAnswerForm(forms.ModelForm):
    def __init__(self, question, session, *args, **kwargs) -> None:
        self.question = question
        super(QuestionAnswerForm, self).__init__(*args, **kwargs)
        if question:
            if question.question_type == "MULTIPLE_CHOICE":
                del self.fields["short_answer"]
                self.fields["multiple_choice"] = forms.ModelMultipleChoiceField(
                    widget=forms.CheckboxSelectMultiple(
                        attrs={
                            "class": "checked:bg-blue-500 checked:border-transparent checked:text-blue-600 rounded focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-1 p-2 pointer-events-none me-2"
                        },
                    ),
                    initial=cache.get(
                        f"{session.session_key}_{self.question.id}_answer"
                    ),
                    queryset=MultipleChoice.objects.filter(question=question),
                )
            elif question.question_type == "SHORT_ANSWER":
                self.fields["short_answer"].initial = cache.get(
                    f"{session.session_key}_{self.question.id}_answer"
                )
                del self.fields["multiple_choice"]

    def save_answer(self, user):
        self.instance.user = user
        self.instance.question = self.question
        self.save()

    def cache_answer(self, session):
        question_type = self.question.question_type.lower()
        answer = self.cleaned_data.get(question_type)

        if self.question.question_type == "MULTIPLE_CHOICE":
            answer = [c.id for c in answer]

        cache.set(f"{session.session_key}_{self.question.id}_answer", answer)
        session[f"{self.question.id}_answer"] = answer

    def clean(self) -> dict[str, Any]:
        cleaned_data = super().clean()
        # check if no choice is selected or no short answer is provided
        if self.question.question_type == "MULTIPLE_CHOICE":
            if not cleaned_data.get("multiple_choice"):
                raise forms.ValidationError("Please select a choice")
        elif self.question.question_type == "SHORT_ANSWER":
            if not cleaned_data.get("short_answer"):
                raise forms.ValidationError("Please provide a short answer")

        return cleaned_data

    class Meta:
        model = QuestionAnswer
        fields = ("multiple_choice", "short_answer")
        widgets = {
            "short_answer": forms.TextInput(
                attrs={
                    "placeholder": "Enter answer",
                    "class": "border bg-white px-4 py-2 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent",
                }
            )
        }
