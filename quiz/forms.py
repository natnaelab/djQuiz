from django import forms
from django.urls import reverse
from .models import Quiz, Question, Choice


class BaseStyledModelForm(forms.ModelForm):
    default_widget_attrs = {
        "class": "border border-gray-400 bg-white px-4 py-2 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
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

    def __init__(self, *args, **kwargs) -> None:
        super(QuizForm, self).__init__(*args, **kwargs)
        title_field = self.fields.get("title")
        description_field = self.fields.get("description")
        title_field.widget.attrs["placeholder"] = "Enter Quiz Title"
        description_field.widget.attrs["class"] += " h-28"
        description_field.widget.attrs["placeholder"] = "Enter Description"


class ChoiceForm(BaseStyledModelForm):
    class Meta:
        model = Choice
        fields = ("text", "is_correct")

    def __init__(self, *args, **kwargs) -> None:
        super(ChoiceForm, self).__init__(*args, **kwargs)

        text_field = self.fields.get("text")
        text_field.label = ""
        text_field.widget.attrs["placeholder"] = f"Enter choice"

        correct_field = self.fields.get("is_correct")
        correct_field.widget.attrs["class"] += " w-full"


class BaseChoiceFormSet(forms.BaseFormSet):
    def __init__(self, *args, **kwargs):
        super(BaseChoiceFormSet, self).__init__(*args, **kwargs)


class QuestionForm(BaseStyledModelForm):
    ChoiceFormSet = forms.formset_factory(
        ChoiceForm,
        formset=BaseChoiceFormSet,
        min_num=2,
        max_num=10,
        extra=0,
        validate_max=True,
    )

    class Meta:
        model = Question
        fields = (
            "question_type",
            "text",
            "duration",
            "correct_short_answer",
            "explanation",
        )

    def __init__(self, *args, **kwargs) -> None:
        super(QuestionForm, self).__init__(*args, **kwargs)
        text_field = self.fields.get("text")
        text_field.widget.attrs["placeholder"] = "Enter question text"
        text_field.widget.attrs["class"] += " h-14"

        correct_short_answer_field = self.fields.get("correct_short_answer")
        correct_short_answer_field.widget.attrs["placeholder"] = "Enter answer"
