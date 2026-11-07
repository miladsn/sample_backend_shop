from django.contrib.auth import get_user_model
from django.test import RequestFactory, TestCase
from django.http import QueryDict
from django.template.loader import render_to_string

from shop.forms import ProductForm
from shop.models import Product, Tag


class ProductTagsTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.tag = Tag.objects.create(title="برچسب نمونه")
        cls.product = Product.objects.create(title="محصول نمونه", slug="test-product")
        cls.product.tags.add(cls.tag)

    def product_data(self, tags):
        data = QueryDict(mutable=True)
        data.update({
            "title": self.product.title,
            "slug": self.product.slug,
            "price": "0",
            "stock": "0",
            "status": "draft",
        })
        data.setlist("tags", tags)
        return data

    def test_existing_tags_are_available_on_create_form(self):
        html = str(ProductForm()["tags"])
        self.assertInHTML(
            f'<option value="{self.tag.pk}">{self.tag.title}</option>', html
        )

    def test_saved_tags_are_selected_on_edit_form(self):
        html = str(ProductForm(instance=self.product)["tags"])
        self.assertInHTML(
            f'<option value="{self.tag.pk}" selected>{self.tag.title}</option>', html
        )

    def test_existing_and_new_tags_are_saved_and_reloaded(self):
        form = ProductForm(
            self.product_data([str(self.tag.pk), "برچسب جدید"]),
            instance=self.product,
        )
        self.assertTrue(form.is_valid(), form.errors)
        product = form.save(commit=False)
        product.save()
        form.save_m2m()
        product.refresh_from_db()
        self.assertSetEqual(
            set(product.tags.values_list("title", flat=True)),
            {self.tag.title, "برچسب جدید"},
        )
        html = str(ProductForm(instance=product)["tags"])
        for tag in product.tags.all():
            self.assertInHTML(
                f'<option value="{tag.pk}" selected>{tag.title}</option>', html
            )

    def test_new_tag_selection_survives_invalid_form(self):
        data = self.product_data([str(self.tag.pk), "برچسب جدید"])
        data["title"] = ""
        form = ProductForm(data, instance=self.product)
        self.assertFalse(form.is_valid())
        html = str(form["tags"])
        self.assertInHTML('<option value="برچسب جدید" selected>برچسب جدید</option>', html)
        self.assertInHTML(
            f'<option value="{self.tag.pk}" selected>{self.tag.title}</option>', html
        )

    def test_tags_can_be_cleared(self):
        form = ProductForm(self.product_data([]), instance=self.product)
        self.assertTrue(form.is_valid(), form.errors)
        product = form.save()
        self.assertFalse(product.tags.exists())

    def test_saved_tags_appear_in_product_list(self):
        request = RequestFactory().get("/cms/shop/products/")
        request.user = get_user_model()(email="tags-test@example.com")
        html = render_to_string(
            "shop/product_list.html",
            {"products": [self.product], "request": request},
        )
        self.assertIn(self.tag.title, html)
