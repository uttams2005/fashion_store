from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Sum
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .models import Product, Category, Cart, Order, OrderItem, UserProfile, Address, PaymentMethod, Review
from .forms import UserRegistrationForm, UserProfileForm, CartUpdateForm, CheckoutForm, PasswordChangeForm, AddressForm, PaymentMethodForm, NotificationPreferencesForm
from django.template.loader import get_template
from django.http import HttpResponse
from django.conf import settings
import os
from xhtml2pdf import pisa


# Single order invoice PDF download view
@login_required
def download_single_order_invoice_pdf(request, order_id):
    from .models import Order, UserProfile
    order = Order.objects.get(id=order_id, user=request.user)
    user_profile = UserProfile.objects.get(user=request.user)
    logo_url = os.path.join(settings.STATIC_ROOT, 'images', 'default-product.jpg')  # Change to your logo path
    template = get_template('store/order_invoice_pdf.html')
    html = template.render({
        'orders': [order],
        'user': request.user,
        'profile': user_profile,
        'logo_url': logo_url,
        'site_name': 'Fashion Store',
    })
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="order_{order.id}_invoice.pdf"'
    pisa_status = pisa.CreatePDF(html, dest=response)
    if pisa_status.err:
        return HttpResponse('We had some errors with PDF generation <br>' + html)
    return response


def home(request):
    products = Product.objects.filter(is_active=True).order_by('id')
    categories = Category.objects.all()
    
    # Search functionality
    query = request.GET.get('q')
    if query:
        products = products.filter(
            Q(name__icontains=query) | Q(description__icontains=query)
        )
    
    # Category filter
    category_id = request.GET.get('category')
    if category_id:
        products = products.filter(category_id=category_id)
    
    # Pagination
    paginator = Paginator(products, 12)  # Show 12 products per page
    page_number = request.GET.get('page')
    
    try:
        page_obj = paginator.page(page_number)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page
        page_obj = paginator.page(1)
    except EmptyPage:
        # If page is out of range, deliver last page of results
        page_obj = paginator.page(paginator.num_pages)
    
    context = {
        'products': page_obj,  # Use page_obj instead of products queryset
        'categories': categories,
        'query': query,
        'selected_category': category_id,
        'page_obj': page_obj  # Also pass page_obj for pagination controls
    }
    return render(request, 'store/home.html', context)

from .forms import ReviewForm

def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id, is_active=True)
    reviews = product.reviews.all()
    user_review = None
    if request.user.is_authenticated:
        try:
            user_review = Review.objects.get(user=request.user, product=product)
        except Review.DoesNotExist:
            user_review = None

    if request.method == 'POST':
        if not request.user.is_authenticated:
            messages.error(request, 'You must be logged in to submit a review.')
            return redirect('login')
        form = ReviewForm(request.POST)
        if form.is_valid():
            review, created = Review.objects.update_or_create(
                user=request.user,
                product=product,
                defaults={
                    'rating': form.cleaned_data['rating'],
                    'comment': form.cleaned_data['comment']
                }
            )
            messages.success(request, 'Your review has been submitted.')
            return redirect('product_detail', product_id=product_id)
    else:
        form = ReviewForm(instance=user_review)

    context = {
        'product': product,
        'reviews': reviews,
        'form': form,
        'user_review': user_review,
    }
    return render(request, 'store/product_detail.html', context)

def user_register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            UserProfile.objects.create(user=user)
            messages.success(request, 'Account created successfully! Please log in.')
            return redirect('login')
    else:
        form = UserRegistrationForm()
    
    context = {'form': form}
    return render(request, 'store/register.html', context)

def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, f'Welcome back, {user.username}!')
            return redirect('home')
        else:
            messages.error(request, 'Invalid username or password.')
    
    return render(request, 'store/login.html')

def user_logout(request):
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('home')

@login_required
def cart_view(request):
    cart_items = Cart.objects.filter(user=request.user)
    total = sum(item.total_price for item in cart_items)
    
    context = {
        'cart_items': cart_items,
        'total': total
    }
    return render(request, 'store/cart.html', context)

@login_required
@require_POST
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    quantity = int(request.POST.get('quantity', 1))
    
    if quantity <= 0:
        messages.error(request, 'Quantity must be greater than 0.')
        return redirect('product_detail', product_id=product_id)
    
    cart_item, created = Cart.objects.get_or_create(
        user=request.user,
        product=product,
        defaults={'quantity': quantity}
    )
    
    if not created:
        cart_item.quantity += quantity
        cart_item.save()
    
    messages.success(request, f'{product.name} added to cart!')
    return redirect('cart')

@login_required
@require_POST
def update_cart(request, cart_id):
    cart_item = get_object_or_404(Cart, id=cart_id, user=request.user)
    quantity = int(request.POST.get('quantity', 1))
    
    if quantity <= 0:
        cart_item.delete()
        messages.success(request, 'Item removed from cart.')
    else:
        cart_item.quantity = quantity
        cart_item.save()
        messages.success(request, 'Cart updated successfully.')
    
    return redirect('cart')

@login_required
@require_POST
def remove_from_cart(request, cart_id):
    cart_item = get_object_or_404(Cart, id=cart_id, user=request.user)
    cart_item.delete()
    messages.success(request, 'Item removed from cart.')
    return redirect('cart')

@login_required
def checkout(request):
    cart_items = Cart.objects.filter(user=request.user)
    
    if not cart_items.exists():
        messages.error(request, 'Your cart is empty.')
        return redirect('cart')
    
    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        if form.is_valid():
            # Create order
            total_price = sum(item.total_price for item in cart_items)
            order = Order.objects.create(
                user=request.user,
                total_price=total_price,
                shipping_address=form.cleaned_data['shipping_address']
            )
            
            # Create order items
            for cart_item in cart_items:
                OrderItem.objects.create(
                    order=order,
                    product=cart_item.product,
                    quantity=cart_item.quantity,
                    price=cart_item.product.price
                )
            
            # Clear cart
            cart_items.delete()
            
            messages.success(request, f'Order placed successfully! Order #: {order.id}')
            return redirect('order_confirmation', order_id=order.id)
    else:
        form = CheckoutForm()
    
    total = sum(item.total_price for item in cart_items)
    context = {
        'form': form,
        'cart_items': cart_items,
        'total': total
    }
    return render(request, 'store/checkout.html', context)

@login_required
def order_confirmation(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    context = {
        'order': order
    }
    return render(request, 'store/order_confirmation.html', context)

@login_required
def order_history(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    context = {
        'orders': orders
    }
    return render(request, 'store/order_history.html', context)

@login_required
def profile_view(request):
    """View user profile"""
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    # Get user's order statistics
    orders = Order.objects.filter(user=request.user)
    total_orders = orders.count()
    total_spent = orders.aggregate(total=Sum('total_price'))['total'] or 0
    
    context = {
        'profile': profile,
        'total_orders': total_orders,
        'total_spent': total_spent,
        'recent_orders': orders.order_by('-created_at')[:5]
    }
    return render(request, 'store/profile.html', context)

@login_required
def profile_edit(request):
    """Edit user profile"""
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('profile_view')
    else:
        form = UserProfileForm(instance=profile)
    
    context = {
        'form': form,
        'profile': profile
    }
    return render(request, 'store/profile_edit.html', context)

@login_required
def change_password(request):
    """Change user password"""
    from django.contrib.auth import update_session_auth_hash
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = request.user
            user.set_password(form.cleaned_data['new_password'])
            user.save()
            # Update session to prevent logout
            update_session_auth_hash(request, user)
            messages.success(request, 'Password changed successfully!')
            return redirect('profile_view')
    else:
        form = PasswordChangeForm(request.user)
    
    context = {
        'form': form
    }
    return render(request, 'store/change_password.html', context)

@login_required
def wishlist_view(request):
    """View user wishlist"""
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    wishlist_items = profile.wishlist.all()
    
    context = {
        'wishlist_items': wishlist_items,
        'profile': profile
    }
    return render(request, 'store/wishlist.html', context)

@login_required
@require_POST
def add_to_wishlist(request, product_id):
    """Add product to wishlist"""
    product = get_object_or_404(Product, id=product_id, is_active=True)
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    if product in profile.wishlist.all():
        messages.info(request, f'{product.name} is already in your wishlist.')
    else:
        profile.wishlist.add(product)
        messages.success(request, f'{product.name} added to wishlist!')
    
    return redirect('product_detail', product_id=product_id)

@login_required
@require_POST
def remove_from_wishlist(request, product_id):
    """Remove product from wishlist"""
    product = get_object_or_404(Product, id=product_id)
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    if product in profile.wishlist.all():
        profile.wishlist.remove(product)
        messages.success(request, f'{product.name} removed from wishlist.')
    else:
        messages.info(request, f'{product.name} is not in your wishlist.')
    
    return redirect('wishlist_view')

@login_required
def address_book(request):
    """View and manage user addresses"""
    addresses = Address.objects.filter(user=request.user)
    
    context = {
        'addresses': addresses
    }
    return render(request, 'store/address_book.html', context)

@login_required
def add_address(request):
    """Add new address"""
    if request.method == 'POST':
        form = AddressForm(request.POST)
        if form.is_valid():
            address = form.save(commit=False)
            address.user = request.user
            
            # If setting as default, remove default from other addresses
            if address.is_default:
                Address.objects.filter(user=request.user, is_default=True).update(is_default=False)
            
            address.save()
            messages.success(request, 'Address added successfully!')
            return redirect('address_book')
    else:
        form = AddressForm()
    
    context = {
        'form': form
    }
    return render(request, 'store/add_address.html', context)

@login_required
def edit_address(request, address_id):
    """Edit existing address"""
    address = get_object_or_404(Address, id=address_id, user=request.user)
    
    if request.method == 'POST':
        form = AddressForm(request.POST, instance=address)
        if form.is_valid():
            address = form.save(commit=False)
            
            # If setting as default, remove default from other addresses
            if address.is_default:
                Address.objects.filter(user=request.user, is_default=True).exclude(id=address_id).update(is_default=False)
            
            address.save()
            messages.success(request, 'Address updated successfully!')
            return redirect('address_book')
    else:
        form = AddressForm(instance=address)
    
    context = {
        'form': form,
        'address': address
    }
    return render(request, 'store/edit_address.html', context)

@login_required
@require_POST
def delete_address(request, address_id):
    """Delete address"""
    address = get_object_or_404(Address, id=address_id, user=request.user)
    address.delete()
    messages.success(request, 'Address deleted successfully!')
    return redirect('address_book')

@login_required
def payment_methods(request):
    """View and manage user payment methods"""
    payment_methods = PaymentMethod.objects.filter(user=request.user)
    
    context = {
        'payment_methods': payment_methods
    }
    return render(request, 'store/payment_methods.html', context)

@login_required
def add_payment_method(request):
    """Add new payment method"""
    if request.method == 'POST':
        form = PaymentMethodForm(request.POST)
        if form.is_valid():
            payment_method = form.save(commit=False)
            payment_method.user = request.user
            
            # If setting as default, remove default from other payment methods
            if payment_method.is_default:
                PaymentMethod.objects.filter(user=request.user, is_default=True).update(is_default=False)
            
            payment_method.save()
            messages.success(request, 'Payment method added successfully!')
            return redirect('payment_methods')
    else:
        form = PaymentMethodForm()
    
    context = {
        'form': form
    }
    return render(request, 'store/add_payment_method.html', context)

@login_required
def edit_payment_method(request, payment_method_id):
    """Edit existing payment method"""
    payment_method = get_object_or_404(PaymentMethod, id=payment_method_id, user=request.user)
    
    if request.method == 'POST':
        form = PaymentMethodForm(request.POST, instance=payment_method)
        if form.is_valid():
            payment_method = form.save(commit=False)
            
            # If setting as default, remove default from other payment methods
            if payment_method.is_default:
                PaymentMethod.objects.filter(user=request.user, is_default=True).exclude(id=payment_method_id).update(is_default=False)
            
            payment_method.save()
            messages.success(request, 'Payment method updated successfully!')
            return redirect('payment_methods')
    else:
        form = PaymentMethodForm(instance=payment_method)
    
    context = {
        'form': form,
        'payment_method': payment_method
    }
    return render(request, 'store/edit_payment_method.html', context)

@login_required
@require_POST
def delete_payment_method(request, payment_method_id):
    """Delete payment method"""
    payment_method = get_object_or_404(PaymentMethod, id=payment_method_id, user=request.user)
    payment_method.delete()
    messages.success(request, 'Payment method deleted successfully!')
    return redirect('payment_methods')

@login_required
def notification_preferences(request):
    """View and manage notification preferences"""
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        form = NotificationPreferencesForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Notification preferences updated successfully!')
            return redirect('notification_preferences')
    else:
        form = NotificationPreferencesForm(instance=profile)
    
    context = {
        'form': form,
        'profile': profile
    }
    return render(request, 'store/notification_preferences.html', context)
