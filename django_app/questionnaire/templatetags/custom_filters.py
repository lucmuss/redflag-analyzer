"""
Custom Template Filters für Questionnaire
"""
from django import template

register = template.Library()


@register.filter
def get_item(dictionary, key):
    """
    Template filter um dict item per key zu holen.
    Usage: {{ my_dict|get_item:key_variable }}
    """
    if dictionary is None:
        return None
    return dictionary.get(key)
