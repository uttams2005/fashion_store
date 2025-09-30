from .models import Category

def categories_processor(request):
    """Add categories to all template contexts"""
    return {
        'categories': Category.objects.all()
    }
