from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Product, Category, UserProfile, Address, PaymentMethod, Review
import json

class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')

class UserProfileForm(forms.ModelForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    
    class Meta:
        model = UserProfile
        fields = ('phone', 'address', 'date_of_birth', 'gender', 'bio', 'website', 
                 'twitter', 'instagram', 'facebook', 'profile_picture',
                 'email_notifications', 'newsletter_subscription')
        widgets = {
            'address': forms.Textarea(attrs={'rows': 3}),
            'bio': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Tell us about yourself...'}),
            'date_of_birth': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'gender': forms.Select(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.user:
            self.fields['email'].initial = self.instance.user.email
            self.fields['first_name'].initial = self.instance.user.first_name
            self.fields['last_name'].initial = self.instance.user.last_name
    
    def save(self, commit=True):
        profile = super().save(commit=False)
        if commit:
            profile.user.email = self.cleaned_data['email']
            profile.user.first_name = self.cleaned_data['first_name']
            profile.user.last_name = self.cleaned_data['last_name']
            profile.user.save()
            profile.save()
        return profile

class PasswordChangeForm(forms.Form):
    current_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        required=True,
        label="Current Password"
    )
    new_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        required=True,
        label="New Password",
        min_length=8
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        required=True,
        label="Confirm New Password"
    )
    
    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)
    
    def clean(self):
        cleaned_data = super().clean()
        new_password = cleaned_data.get('new_password')
        confirm_password = cleaned_data.get('confirm_password')
        current_password = cleaned_data.get('current_password')
        
        if new_password and confirm_password and new_password != confirm_password:
            self.add_error('confirm_password', "Passwords do not match")
        
        if current_password and not self.user.check_password(current_password):
            self.add_error('current_password', "Current password is incorrect")
        
        return cleaned_data

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'description', 'price', 'category', 'image', 'stock', 'is_active']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'price': forms.NumberInput(attrs={'step': '0.01', 'min': '0.01'}),
        }

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }

class CartUpdateForm(forms.Form):
    quantity = forms.IntegerField(min_value=1, widget=forms.NumberInput(attrs={'class': 'form-control'}))

class CheckoutForm(forms.Form):
    shipping_address = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
        required=True
    )
    phone = forms.CharField(max_length=15, required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))

class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = ['address_type', 'full_name', 'phone', 'street_address', 'city', 'state', 'postal_code', 'country', 'is_default']
        widgets = {
            'street_address': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'address_type': forms.Select(attrs={'class': 'form-control'}),
            'full_name': forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'state': forms.TextInput(attrs={'class': 'form-control'}),
            'postal_code': forms.TextInput(attrs={'class': 'form-control'}),
            'country': forms.TextInput(attrs={'class': 'form-control'}),
            'is_default': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class PaymentMethodForm(forms.ModelForm):
    class Meta:
        model = PaymentMethod
        fields = ['payment_type', 'is_default']
        widgets = {
            'payment_type': forms.Select(attrs={'class': 'form-control'}),
            'is_default': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Dynamically add fields based on payment type
        if self.instance and self.instance.pk:
            payment_type = self.instance.payment_type
        else:
            payment_type = self.data.get('payment_type') if self.data else None
        
        if payment_type in ['credit_card', 'debit_card']:
            self.fields['card_number'] = forms.CharField(
                max_length=19, required=True,
                widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '1234 5678 9012 3456'})
            )
            self.fields['card_holder_name'] = forms.CharField(
                max_length=100, required=True,
                widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'John Doe'})
            )
            self.fields['expiry_month'] = forms.IntegerField(
                min_value=1, max_value=12, required=True,
                widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'MM'})
            )
            self.fields['expiry_year'] = forms.IntegerField(
                min_value=2023, max_value=2100, required=True,
                widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'YYYY'})
            )
            self.fields['cvv'] = forms.CharField(
                max_length=4, required=True,
                widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': '123'})
            )
        elif payment_type == 'upi':
            self.fields['upi_id'] = forms.CharField(
                max_length=50, required=True,
                widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'username@upi'})
            )
        elif payment_type == 'net_banking':
            self.fields['bank_name'] = forms.CharField(
                max_length=100, required=True,
                widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Bank Name'})
            )
            self.fields['account_number'] = forms.CharField(
                max_length=20, required=True,
                widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Account Number'})
            )
            self.fields['ifsc_code'] = forms.CharField(
                max_length=11, required=True,
                widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'IFSC Code'})
            )

class NotificationPreferencesForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['notification_preferences']
        widgets = {
            'notification_preferences': forms.HiddenInput(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Create checkbox fields for each notification preference
        preferences = self.instance.NOTIFICATION_PREFERENCES if self.instance else UserProfile.NOTIFICATION_PREFERENCES

        for pref_key, default_value in preferences.items():
            field_name = f'notify_{pref_key}'
            self.fields[field_name] = forms.BooleanField(
                required=False,
                initial=self.instance.notification_preferences.get(pref_key, default_value) if self.instance else default_value,
                label=pref_key.replace('_', ' ').title(),
                widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
            )

    def save(self, commit=True):
        profile = super().save(commit=False)
        preferences = {}

        for field_name, value in self.cleaned_data.items():
            if field_name.startswith('notify_'):
                pref_key = field_name.replace('notify_', '')
                preferences[pref_key] = value

        profile.notification_preferences = preferences

        if commit:
            profile.save()

        return profile

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'comment']
        widgets = {
            'rating': forms.Select(choices=[(i, i) for i in range(1, 6)], attrs={'class': 'form-select'}),
            'comment': forms.Textarea(attrs={'rows': 3, 'class': 'form-control', 'placeholder': 'Write your review here...'}),
        }
