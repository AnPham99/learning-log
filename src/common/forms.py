"""Shared accessible widget presentation; no validation or persistence here."""

from django import forms


def style_fields(form: forms.Form) -> None:
    for name, field in form.fields.items():
        field.widget.attrs["class"] = "form-input"
        if name == "username":
            field.widget.attrs.update({"autocapitalize": "none", "autocomplete": "username"})
        if name.startswith("password"):
            field.widget.attrs["autocomplete"] = (
                "current-password" if name == "password" else "new-password"
            )
