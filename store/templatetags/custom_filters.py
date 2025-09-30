from django import template
from store.models import Category

register = template.Library()

@register.simple_tag
def get_categories():
    """Return all categories for use in templates"""
    return Category.objects.all()
