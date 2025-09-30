from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.db.models import Count, Sum, Q
from django.utils import timezone
from datetime import timedelta
from store.models import Product, Category, Order, OrderItem
from store.forms import ProductForm, CategoryForm

def is_admin(user):
    return user.is_authenticated and user.is_staff

@login_required
@user_passes_test(is_admin)
def admin_dashboard(request):
    # Get statistics
    total_users = User.objects.count()
    total_products = Product.objects.count()
    total_orders = Order.objects.count()
    
    # Recent orders
    recent_orders = Order.objects.select_related('user').order_by('-created_at')[:5]
    
    # Sales statistics (last 30 days)
    thirty_days_ago = timezone.now() - timedelta(days=30)
    recent_sales = Order.objects.filter(
        created_at__gte=thirty_days_ago,
        status__in=['delivered', 'shipped']
    ).aggregate(total_sales=Sum('total_price'))['total_sales'] or 0

    # Additional statistics for dashboard
    active_products_count = Product.objects.filter(is_active=True).count()
    categories_with_products_count = Category.objects.annotate(product_count=Count('products')).filter(product_count__gt=0).count()
    empty_categories_count = Category.objects.annotate(product_count=Count('products')).filter(product_count=0).count()
    pending_orders_count = Order.objects.filter(status='pending').count()
    processing_orders_count = Order.objects.filter(status='processing').count()
    delivered_orders_count = Order.objects.filter(status='delivered').count()
    
    context = {
        'total_users': total_users,
        'total_products': total_products,
        'total_orders': total_orders,
        'recent_sales': recent_sales,
        'recent_orders': recent_orders,
        'active_products_count': active_products_count,
        'categories_with_products_count': categories_with_products_count,
        'empty_categories_count': empty_categories_count,
        'pending_orders_count': pending_orders_count,
        'processing_orders_count': processing_orders_count,
        'delivered_orders_count': delivered_orders_count,
    }
    return render(request, 'admin_dashboard/dashboard.html', context)

@login_required
@user_passes_test(is_admin)
def user_management(request):
    users_list = User.objects.all().order_by('-date_joined')
    
    # Search functionality
    search_query = request.GET.get('search')
    if search_query:
        users_list = users_list.filter(
            Q(username__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query)
        )
    
    # Filter functionality
    status_filter = request.GET.get('status_filter')
    if status_filter:
        if status_filter == 'active':
            users_list = users_list.filter(is_active=True)
        elif status_filter == 'inactive':
            users_list = users_list.filter(is_active=False)
        elif status_filter == 'staff':
            users_list = users_list.filter(is_staff=True)
        elif status_filter == 'superuser':
            users_list = users_list.filter(is_superuser=True)
    
    # Pagination
    paginator = Paginator(users_list, 10)  # Show 10 users per page
    page_number = request.GET.get('page')
    users = paginator.get_page(page_number)
    
    # Calculate user statistics
    total_users = users_list.count()
    active_users = users_list.filter(is_active=True).count()
    inactive_users = total_users - active_users
    
    if request.method == 'POST':
        # Handle bulk actions
        if 'bulk_action' in request.POST and 'user_ids' in request.POST:
            bulk_action = request.POST.get('bulk_action')
            user_ids = request.POST.getlist('user_ids')
            
            if bulk_action and user_ids:
                users_to_update = User.objects.filter(id__in=user_ids)
                
                if bulk_action == 'activate':
                    users_to_update.update(is_active=True)
                    messages.success(request, f'{len(user_ids)} users activated successfully.')
                elif bulk_action == 'deactivate':
                    users_to_update.update(is_active=False)
                    messages.success(request, f'{len(user_ids)} users deactivated successfully.')
                elif bulk_action == 'delete':
                    users_to_update.delete()
                    messages.success(request, f'{len(user_ids)} users deleted successfully.')
        
        # Handle individual actions
        elif 'user_id' in request.POST and 'action' in request.POST:
            user_id = request.POST.get('user_id')
            action = request.POST.get('action')
            
            if user_id and action:
                user = get_object_or_404(User, id=user_id)
                
                if action == 'activate':
                    user.is_active = True
                    user.save()
                    messages.success(request, f'User {user.username} activated successfully.')
                elif action == 'deactivate':
                    user.is_active = False
                    user.save()
                    messages.success(request, f'User {user.username} deactivated successfully.')
                elif action == 'delete':
                    user.delete()
                    messages.success(request, f'User {user.username} deleted successfully.')
    
    context = {
        'users': users,
        'total_users': total_users,
        'active_users': active_users,
        'inactive_users': inactive_users
    }
    return render(request, 'admin_dashboard/user_management.html', context)

@login_required
@user_passes_test(is_admin)
def product_management(request):
    products_list = Product.objects.select_related('category').all().order_by('-created_at')

    # Pagination
    paginator = Paginator(products_list, 10)  # Show 10 products per page
    page_number = request.GET.get('page')
    products = paginator.get_page(page_number)
    
    # Calculate statistics from the full queryset
    total_products = products_list.count()
    active_products_count = products_list.filter(is_active=True).count()
    distinct_categories_count = products_list.values_list('category', flat=True).distinct().count()
    in_stock_products_count = products_list.filter(stock__gt=0).count()
    
    context = {
    'products': products,
    'total_products': total_products,

    'active_products_count': active_products_count,
    'distinct_categories_count': distinct_categories_count,
    'in_stock_products_count': in_stock_products_count,
    }
    return render(request, 'admin_dashboard/product_management.html', context)

@login_required
@user_passes_test(is_admin)
def add_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Product added successfully!')
            return redirect('admin_product_management')
    else:
        form = ProductForm()
    
    context = {
        'form': form,
        'action': 'Add'
    }
    return render(request, 'admin_dashboard/product_form.html', context)

@login_required
@user_passes_test(is_admin)
def edit_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, 'Product updated successfully!')
            return redirect('admin_product_management')
    else:
        form = ProductForm(instance=product)
    
    context = {
        'form': form,
        'product': product,
        'action': 'Edit'
    }
    return render(request, 'admin_dashboard/product_form.html', context)

@login_required
@user_passes_test(is_admin)
def delete_product(request, product_id):
    if request.method == 'POST':
        product = get_object_or_404(Product, id=product_id)
        product_name = product.name
        product.delete()
        messages.success(request, f'Product "{product_name}" deleted successfully!')
        return redirect('admin_product_management')
    
    return redirect('admin_product_management')

@login_required
@user_passes_test(is_admin)
def category_management(request):
    categories = Category.objects.all().order_by('-created_at')

    categories_with_products_count = categories.annotate(product_count=Count('products')).filter(product_count__gt=0).count()
    empty_categories_count = categories.annotate(product_count=Count('products')).filter(product_count=0).count()
    
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Category added successfully!')
            return redirect('admin_category_management')
    else:
        form = CategoryForm()
    
    context = {
        'categories': categories,
        'form': form,
        'categories_with_products_count': categories_with_products_count,
        'empty_categories_count': empty_categories_count,
    }
    return render(request, 'admin_dashboard/category_management.html', context)

@login_required
@user_passes_test(is_admin)
def edit_category(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, 'Category updated successfully!')
            return redirect('admin_category_management')
    else:
        form = CategoryForm(instance=category)
    
    context = {
        'form': form,
        'category': category,
        'action': 'Edit'
    }
    return render(request, 'admin_dashboard/category_form.html', context)

@login_required
@user_passes_test(is_admin)
def delete_category(request, category_id):
    if request.method == 'POST':
        category = get_object_or_404(Category, id=category_id)
        category_name = category.name
        
        # Check if category has products
        if category.products.exists():
            messages.error(request, f'Cannot delete category "{category_name}" - it has associated products.')
        else:
            category.delete()
            messages.success(request, f'Category "{category_name}" deleted successfully!')
        
        return redirect('admin_category_management')
    
    return redirect('admin_category_management')

@login_required
@user_passes_test(is_admin)
def order_management(request):
    orders_list = Order.objects.select_related('user').all().order_by('-created_at')

    # Pagination
    paginator = Paginator(orders_list, 10)  # Show 10 orders per page
    page_number = request.GET.get('page')
    orders = paginator.get_page(page_number)
    
    # Calculate statistics from the full queryset
    pending_count = orders_list.filter(status='pending').count()
    processing_count = orders_list.filter(status='processing').count()
    delivered_count = orders_list.filter(status='delivered').count()
    
    if request.method == 'POST':
        order_id = request.POST.get('order_id')
        new_status = request.POST.get('status')
        
        if order_id and new_status:
            order = get_object_or_404(Order, id=order_id)
            order.status = new_status
            order.save()
            messages.success(request, f'Order #{order_id} status updated to {new_status}.')
    
    context = {
        'orders': orders,
        'pending_count': pending_count,
        'processing_count': processing_count,
        'delivered_count': delivered_count,
    }
    return render(request, 'admin_dashboard/order_management.html', context)
