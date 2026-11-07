from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient

from shop.models import Category, Product, ProductStatus, Tag


class ProductSearchFilterTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.client.force_authenticate(get_user_model().objects.create_user(username='filter-owner'))
        self.parent = Category.objects.create(name='کنسول', slug='console')
        self.child = Category.objects.create(name='پلی استیشن', slug='playStation', parent=self.parent)
        self.leaf = Category.objects.create(name='مدل جدید', slug='new-console', parent=self.child)
        self.tag = Tag.objects.create(title='بازی ویدیویی')
        self.product = Product.objects.create(title='کنسول بازی', slug='console-test', status=ProductStatus.PUBLISHED)
        self.product.categories.add(self.leaf)
        self.product.tags.add(self.tag)

    def product_ids(self, **params):
        response = self.client.get('/api/v1/shop/products/', params)
        self.assertEqual(response.status_code, 200)
        return [item['id'] for item in response.data]

    def test_parent_category_includes_nested_products(self):
        self.assertEqual(self.product_ids(categories='console'), [self.product.pk])
        self.assertEqual(self.product_ids(category='console'), [self.product.pk])

    def test_real_tag_title_and_legacy_slug_both_work(self):
        self.assertEqual(self.product_ids(tags='بازی ویدیویی'), [self.product.pk])
        self.assertEqual(self.product_ids(tags=self.tag.slug), [self.product.pk])
        self.assertEqual(self.tag.slug, 'بازی-ویدیویی')

    def test_category_and_tag_filters_work_together(self):
        self.assertEqual(self.product_ids(categories='console', tags='بازی ویدیویی'), [self.product.pk])

    def test_inactive_descendants_and_unknown_filters_do_not_expand_search(self):
        self.child.is_active = False
        self.child.save()
        self.assertEqual(self.product_ids(categories='console'), [])
        self.assertEqual(self.product_ids(categories='missing'), [])
        self.assertEqual(self.product_ids(tags='missing'), [])
