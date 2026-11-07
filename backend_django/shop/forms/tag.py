#forms/shop/forms/tag

from django import forms
from django.forms.widgets import  SelectMultiple


# ==========================================
# Product Management Fields and Forms
# ==========================================
class TagsField(forms.Field):
    widget = SelectMultiple

    def to_python(self, value):
        if not value:
            return []
        if isinstance(value, list):
            return value
        return [v.strip() for v in str(value).split(",") if v.strip()]
