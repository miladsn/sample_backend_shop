#forms/shop/forms/product
from django import forms
from django.forms import SelectMultiple

from shop.forms.tag import TagsField
from shop.models import Category, Tag, Product


class LeafCategoryMultipleChoiceField(forms.ModelMultipleChoiceField):
    """Display the final categories along with their full paths."""

    def label_from_instance(self, obj):
        parts = [obj.name]
        parent = obj.parent
        visited = {obj.pk}

        while parent and parent.pk not in visited:
            parts.append(parent.name)
            visited.add(parent.pk)
            parent = parent.parent

        return " / ".join(reversed(parts))


class ProductForm(forms.ModelForm):
    tags = TagsField(
        required=False,
        widget=SelectMultiple(
            attrs={
                "class": "form-control select2-tags",
                "multiple": "multiple",
                "data-placeholder": "انتخاب یا افزودن برچسب...",
            }
        ),
    )
    categories = LeafCategoryMultipleChoiceField(
        queryset=Category.objects.none(),
        required=False,
        widget=SelectMultiple(
            attrs={
                "class": "form-control select2",
                "multiple": "multiple",
                "data-placeholder": "انتخاب دسته‌بندی...",
            }
        ),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Setting tag values in edit mode
        # TagsField is a plain Field, so choices must be set on its widget.
        tag_choices = [(str(t.id), t.title) for t in Tag.objects.all()]
        if self.is_bound:
            known_values = {value for value, _ in tag_choices}
            for value in self.fields["tags"].widget.value_from_datadict(
                self.data, self.files, self.add_prefix("tags")
            ):
                if value and value not in known_values:
                    tag_choices.append((value, value))
                    known_values.add(value)
        self.fields["tags"].widget.choices = tag_choices
        if self.instance and self.instance.pk:
            self.initial["tags"] = list(
                self.instance.tags.values_list("id", flat=True)
            )

        # Only terminal categories (those without children) can be selected for the product.
        # # The active status does not alter the category tree; the criterion for this list
        # is solely whether a category is a terminal (final) one.
        self.fields["categories"].queryset = Category.objects.filter(
            children__isnull=True,
        ).select_related(
            "parent",
            "parent__parent",
            "parent__parent__parent",
        ).order_by("name", "id")

    def clean_tags(self):
        tags_data = self.cleaned_data.get("tags", [])
        tag_objects = []

        for item in tags_data:
            if not item:
                continue

            # Existing tags by ID
            if str(item).isdigit():
                try:
                    tag_obj = Tag.objects.get(pk=int(item))
                    tag_objects.append(tag_obj)
                    continue
                except Tag.DoesNotExist:
                    pass

            # New Text Tags (Create on the fly)
            tag_title = str(item).strip()
            if tag_title:
                slug_candidate = tag_title.replace(" ", "-")
                tag_obj, _ = Tag.objects.get_or_create(
                    title=tag_title,
                    defaults={"slug": slug_candidate},
                )
                tag_objects.append(tag_obj)

        return tag_objects

    class Meta:
        model = Product
        fields = [
            "title",
            "slug",
            "sku",
            "price",
            "sale_price",
            "stock",
            "short_description",
            "description",
            "status",
            "is_featured",
            "meta_title",
            "meta_description",
            "categories",
            "tags",
        ]
        widgets = {
            "title": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "نام محصول"}
            ),
            "slug": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "آدرس محصول",
                    "dir": "ltr",
                }
            ),
            "sku": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "شناسه انبارداری (SKU)",
                    "dir": "ltr",
                }
            ),
            "price": forms.NumberInput(
                attrs={"class": "form-control", "placeholder": "قیمت اصلی"}
            ),
            "sale_price": forms.NumberInput(
                attrs={"class": "form-control", "placeholder": "قیمت با تخفیف"}
            ),
            "stock": forms.NumberInput(
                attrs={"class": "form-control", "placeholder": "تعداد موجودی"}
            ),
            "short_description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "توضیحات کوتاه...",
                }
            ),
            "description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 6,
                    "placeholder": "توضیحات کامل محصول...",
                }
            ),
            "status": forms.Select(attrs={"class": "form-select"}),
            "is_featured": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "meta_title": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "عنوان سئو"}
            ),
            "meta_description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "توضیحات سئو...",
                }
            ),
            "categories": forms.SelectMultiple(
                attrs={
                    "class": "form-control select2",
                    "multiple": "multiple",
                    "data-placeholder": "انتخاب دسته‌بندی...",
                }
            ),
        }
