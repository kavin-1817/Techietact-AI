from django import template

register = template.Library()


@register.filter
def is_admin(user):
    """Check if user is an admin"""
    if not user or not user.is_authenticated:
        return False
    return user.is_staff or hasattr(user, 'admin_profile')


@register.filter
def get_item(dictionary, key):
    """Get an item from a dictionary using a key"""
    if dictionary is None:
        return None
    return dictionary.get(key)
