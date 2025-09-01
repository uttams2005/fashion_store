from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.contrib import messages
from store.models import Product, Category, Order, OrderItem

class AdminDashboardTests(TestCase):
    
    def setUp(self):
        # Create admin user
        self.admin_user = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='testpass123',
            is_staff=True
        )
        
        # Create regular user
        self.regular_user = User.objects.create_user(
            username='regular',
            email='regular@example.com',
            password='testpass123',
            is_staff=False
        )
        
        # Create test category
        self.category = Category.objects.create(
            name='Test Category',
            description='Test category description'
        )
        
        # Create test product
        self.product = Product.objects.create(
            name='Test Product',
            description='Test product description',
            price=99.99,
            stock=10,
            category=self.category,
            is_active=True
        )
        
        # Create test order
        self.order = Order.objects.create(
            user=self.regular_user,
            total_price=99.99,
            shipping_address='Test Address',
            status='pending'
        )
        
        # Create order item
        OrderItem.objects.create(
            order=self.order,
            product=self.product,
            quantity=1,
            price=99.99
        )
        
        self.client = Client()
    
    def test_admin_dashboard_view_requires_login(self):
        """Test that admin dashboard requires login"""
        response = self.client.get(reverse('admin_dashboard'))
        self.assertEqual(response.status_code, 302)  # Redirect to login
    
    def test_admin_dashboard_view_requires_staff(self):
        """Test that admin dashboard requires staff status"""
        self.client.login(username='regular', password='testpass123')
        response = self.client.get(reverse('admin_dashboard'))
        self.assertEqual(response.status_code, 302)  # Redirect to login
    
    def test_admin_dashboard_view_success(self):
        """Test admin dashboard view with staff user"""
        self.client.login(username='admin', password='testpass123')
        response = self.client.get(reverse('admin_dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Dashboard')
        self.assertContains(response, 'Total Users')
        self.assertContains(response, 'Total Products')
        self.assertContains(response, 'Total Orders')
    
    def test_user_management_view(self):
        """Test user management view"""
        self.client.login(username='admin', password='testpass123')
        response = self.client.get(reverse('admin_user_management'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'User Management')
        self.assertContains(response, 'All Users')
    
    def test_user_management_pagination(self):
        """Test user management pagination"""
        # Create more users to test pagination
        for i in range(15):
            User.objects.create_user(
                username=f'testuser{i}',
                email=f'test{i}@example.com',
                password='testpass123'
            )
        
        self.client.login(username='admin', password='testpass123')
        response = self.client.get(reverse('admin_user_management') + '?page=2')
        self.assertEqual(response.status_code, 200)
        # Check that pagination is present and working
        self.assertContains(response, 'pagination')
        self.assertContains(response, 'page=1')
        # Check that page 2 is active in pagination
        self.assertContains(response, '<span class="page-link">2</span>')
    
    def test_product_management_view(self):
        """Test product management view"""
        self.client.login(username='admin', password='testpass123')
        response = self.client.get(reverse('admin_product_management'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Product Management')
        self.assertContains(response, 'All Products')
    
    def test_product_management_pagination(self):
        """Test product management pagination"""
        # Create more products to test pagination
        for i in range(15):
            Product.objects.create(
                name=f'Test Product {i}',
                description=f'Test product {i} description',
                price=10.99 + i,
                stock=5,
                category=self.category,
                is_active=True
            )
        
        self.client.login(username='admin', password='testpass123')
        response = self.client.get(reverse('admin_product_management') + '?page=2')
        self.assertEqual(response.status_code, 200)
        # Check that pagination is present and working
        self.assertContains(response, 'pagination')
        self.assertContains(response, 'page=1')
        # Check that page 2 is active in pagination
        self.assertContains(response, '<span class="page-link">2</span>')
    
    def test_order_management_view(self):
        """Test order management view"""
        self.client.login(username='admin', password='testpass123')
        response = self.client.get(reverse('admin_order_management'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Order Management')
        self.assertContains(response, 'All Orders')
    
    def test_order_management_pagination(self):
        """Test order management pagination"""
        # Create more orders to test pagination
        for i in range(15):
            order = Order.objects.create(
                user=self.regular_user,
                total_price=50.00 + i,
                shipping_address=f'Test Address {i}',
                status='pending'
            )
            OrderItem.objects.create(
                order=order,
                product=self.product,
                quantity=1,
                price=50.00 + i
            )
        
        self.client.login(username='admin', password='testpass123')
        response = self.client.get(reverse('admin_order_management') + '?page=2')
        self.assertEqual(response.status_code, 200)
        # Check that pagination is present and working
        self.assertContains(response, 'pagination')
        self.assertContains(response, 'page=1')
        # Check that page 2 is active in pagination
        self.assertContains(response, '<span class="page-link">2</span>')
    
    def test_user_activation_deactivation(self):
        """Test user activation and deactivation functionality"""
        self.client.login(username='admin', password='testpass123')
        
        # Test deactivation
        response = self.client.post(reverse('admin_user_management'), {
            'user_id': self.regular_user.id,
            'action': 'deactivate'
        })
        self.assertEqual(response.status_code, 200)
        self.regular_user.refresh_from_db()
        self.assertFalse(self.regular_user.is_active)
        
        # Test activation
        response = self.client.post(reverse('admin_user_management'), {
            'user_id': self.regular_user.id,
            'action': 'activate'
        })
        self.assertEqual(response.status_code, 200)
        self.regular_user.refresh_from_db()
        self.assertTrue(self.regular_user.is_active)
    
    def test_order_status_update(self):
        """Test order status update functionality"""
        self.client.login(username='admin', password='testpass123')
        
        response = self.client.post(reverse('admin_order_management'), {
            'order_id': self.order.id,
            'status': 'processing'
        })
        self.assertEqual(response.status_code, 200)
        self.order.refresh_from_db()
        self.assertEqual(self.order.status, 'processing')
    
    def test_dashboard_statistics(self):
        """Test dashboard statistics calculation"""
        self.client.login(username='admin', password='testpass123')
        response = self.client.get(reverse('admin_dashboard'))
        
        # Check that statistics are present in context
        self.assertIn('total_users', response.context)
        self.assertIn('total_products', response.context)
        self.assertIn('total_orders', response.context)
        self.assertIn('active_products_count', response.context)
        self.assertIn('categories_with_products_count', response.context)
        self.assertIn('empty_categories_count', response.context)
        self.assertIn('pending_orders_count', response.context)
        
        # Verify statistics values
        self.assertEqual(response.context['total_users'], 2)  # admin + regular
        self.assertEqual(response.context['total_products'], 1)
        self.assertEqual(response.context['total_orders'], 1)
        self.assertEqual(response.context['active_products_count'], 1)
        self.assertEqual(response.context['categories_with_products_count'], 1)
        self.assertEqual(response.context['empty_categories_count'], 0)
        self.assertEqual(response.context['pending_orders_count'], 1)
