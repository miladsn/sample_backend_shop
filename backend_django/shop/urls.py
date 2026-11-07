# shop/urls.py
from django.urls import path
from . import views
from .views.cart import add_to_cart_view

app_name = 'shop'

urlpatterns = [
    # Categories ...
    path('categories/', views.category_list, name='category_list'),
    path('categories/create/', views.category_create, name='category_create'),
    path('categories/delete/<int:pk>/', views.category_delete, name='category_delete'),
    path(
        "categories/<int:pk>/edit/",
        views.category_update,
        name="category_update",
    ),
    # Products
    path('products/', views.ProductListView.as_view(), name='product_list'),
    path('products/create/', views.product_create, name='product_create'),
    path(
        'products/<int:pk>/update/',
        views.product_update,
        name='product_update'
    ),
    path('products/<int:pk>/delete/', views.ProductDeleteView.as_view(), name='product_delete'),
    # urls.py (inside app_name = 'shop')

    path('products/album/<int:pk>/delete/', views.product.product_album_delete, name='product_album_delete'),

    path('cart/add/', add_to_cart_view, name='add_to_cart'),

]
