from django import forms

from common.forms import style_fields


class TopicForm(forms.Form):
    text = forms.CharField(
        label="Tên chủ đề",
        max_length=200,
        help_text="Một lĩnh vực, một kỹ năng, hoặc một điều bạn muốn hiểu rõ hơn.",
        widget=forms.TextInput(attrs={"placeholder": "Ví dụ: Lập trình Python", "autofocus": True}),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        style_fields(self)


class EntryForm(forms.Form):
    text = forms.CharField(
        label="Hôm nay bạn học được gì?",
        widget=forms.Textarea(
            attrs={
                "rows": 12,
                "placeholder": "Ghi lại ý chính, ví dụ và những điều bạn muốn nhớ…",
                "autofocus": True,
                "data-editor": "true",
            }
        ),
        help_text="Không cần viết hoàn hảo. Một ý tưởng nhỏ cũng là một bước tiến.",
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        style_fields(self)
