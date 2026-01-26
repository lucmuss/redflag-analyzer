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


@register.filter
def replace(value, arg):
    """
    Template filter um String-Ersetzungen durchzuführen.
    Usage: {{ "hello_world"|replace:"_":" " }}
    
    Args:
        value: Der String, in dem ersetzt werden soll
        arg: Format "old:new" oder "old" (dann wird durch Leerzeichen ersetzt)
    """
    if not value:
        return value
    
    # Parse argument - Format: "old:new" oder nur "old"
    if ':' in arg:
        old, new = arg.split(':', 1)
    else:
        old = arg
        new = ' '
    
    return str(value).replace(old, new)
