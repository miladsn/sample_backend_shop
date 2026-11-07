#forms/shop/forms/category
# ==========================================
# Category Management Form
# ==========================================
from django import forms
from django.forms.widgets import CheckboxInput, Select, SelectMultiple, TextInput

from shop.models import Category


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ["name", "slug", "parent", "is_active"]
        widgets = {
            "name": TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "نام دسته‌بندی",
                }
            ),
            "slug": TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "آدرس دسته‌بندی (slug)",
                    "dir": "ltr",
                }
            ),
            "is_active": CheckboxInput(
                attrs={
                    "class": "form-check-input",
                    "id": "is_active",
                }
            ),
            "parent": Select(
                attrs={
                    "class": "form-select",
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Parent is optional (for top-level main categories)
        self.fields["parent"].required = False
        self.fields["parent"].empty_label = "بدون والد (دسته‌بندی اصلی)"

        # In edit mode: Prevent the category itself from being selected in the drop-down
        if self.instance and self.instance.pk:
            self.fields["parent"].queryset = Category.objects.exclude(
                pk=self.instance.pk
            )

    def clean_parent(self):
        parent = self.cleaned_data.get("parent")

        if parent:
            # Preventing the category from becoming its own parent
            if self.instance.pk and parent.pk == self.instance.pk:
                raise forms.ValidationError("یک دسته‌بندی نمی‌تواند والد خودش باشد.")

            # Reviewing category depth (maximum 3 levels: root -> subcategory -> final branch)
            # If the selected parent has a parent of their own, and that parent also has a parent, the depth exceeds 3:
            depth = 1
            current = parent
            while current.parent:
                depth += 1
                current = current.parent
                if depth >= 3:
                    raise forms.ValidationError("امکان ثبت بیش از ۳ سطح دسته‌بندی وجود ندارد.")

            # Preventing the creation of loops during editing
            if self.instance.pk:
                ancestor = parent
                while ancestor:
                    if ancestor.pk == self.instance.pk:
                        raise forms.ValidationError(
                            "نمی‌توانید یکی از زیرمجموعه‌های این دسته را به عنوان والد آن انتخاب کنید.")
                    ancestor = ancestor.parent

        return parent

