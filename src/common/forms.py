from django import forms


class StyledFormMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.setdefault("class", "input")
            if isinstance(field, forms.DecimalField):
                field.widget.attrs.setdefault("min", "0")
