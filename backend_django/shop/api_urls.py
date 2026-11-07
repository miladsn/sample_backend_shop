# shop/urls.py
from django.urls import path

from shop.api_views.category_view import CategoryApiView
from shop.api_views.tag_view import TagApiView
from shop.api_views.product_view import ProductListAPIView
from shop.api_views.search_metadata import SearchMetadataAPIView

urlpatterns = [
    path('search-metadata/', SearchMetadataAPIView.as_view(), name='search-metadata'),
    path('categories/', CategoryApiView.as_view(), name='category_list'),
    path('tags/', TagApiView.as_view(), name='tag_list'),
    # Products Web Service API Route
    path('products/', ProductListAPIView.as_view(), name='api_product_list'),

    # Previous paths for the panel and templates:
    # path('products/', ...),
]
