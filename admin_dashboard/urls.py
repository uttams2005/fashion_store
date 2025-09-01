from django.urls import path
from . import views

urlpatterns = [
    path('', views.admin_dashboard, name='admin_dashboard'),
    path('users/', views.user_management, name='admin_user_management'),
    path('products/', views.product_management, name='admin_product_management'),
    path('products/add/', views.add_product, name='admin_add_product'),
    path('products/edit/<int:product_id>/', views.edit_product, name='admin_edit_product'),
    path('products/delete/<int:product_id>/', views.delete_product, name='admin_delete_product'),
    path('categories/', views.category_management, name='admin_category_management'),
    path('categories/edit/<int:category_id>/', views.edit_category, name='admin_edit_category'),
    path('categories/delete/<int:category_id>/', views.delete_category, name='admin_delete_category'),
    path('orders/', views.order_management, name='admin_order_management'),
]
