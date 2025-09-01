from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('profile/', views.profile_view, name='profile_view'),
    path('profile/edit/', views.profile_edit, name='profile_edit'),
    path('product/<int:product_id>/', views.product_detail, name='product_detail'),
    path('register/', views.user_register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('cart/', views.cart_view, name='cart'),
    path('add-to-cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('update-cart/<int:cart_id>/', views.update_cart, name='update_cart'),
    path('remove-from-cart/<int:cart_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('order-confirmation/<int:order_id>/', views.order_confirmation, name='order_confirmation'),
    path('order-history/', views.order_history, name='order_history'),
    path('change-password/', views.change_password, name='change_password'),
    path('download-invoice/<int:order_id>/', views.download_single_order_invoice_pdf, name='download_single_order_invoice_pdf'),

    
    # Wishlist URLs
    path('wishlist/', views.wishlist_view, name='wishlist_view'),
    path('add-to-wishlist/<int:product_id>/', views.add_to_wishlist, name='add_to_wishlist'),
    path('remove-from-wishlist/<int:product_id>/', views.remove_from_wishlist, name='remove_from_wishlist'),
    
    # Address Book URLs
    path('address-book/', views.address_book, name='address_book'),
    path('address/add/', views.add_address, name='add_address'),
    path('address/edit/<int:address_id>/', views.edit_address, name='edit_address'),
    path('address/delete/<int:address_id>/', views.delete_address, name='delete_address'),
    
    # Payment Methods URLs
    path('payment-methods/', views.payment_methods, name='payment_methods'),
    path('payment-method/add/', views.add_payment_method, name='add_payment_method'),
    path('payment-method/edit/<int:payment_method_id>/', views.edit_payment_method, name='edit_payment_method'),
    path('payment-method/delete/<int:payment_method_id>/', views.delete_payment_method, name='delete_payment_method'),
    
    # Notification Preferences URL
    path('notification-preferences/', views.notification_preferences, name='notification_preferences'),
]
