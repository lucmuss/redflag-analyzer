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


@register.filter
def score_color_class(score):
    """
    Gibt Tailwind-Klassen für Score-basierte Farbkodierung zurück.
    
    Farbschema (FESTE GRENZEN):
    - 0.0-1.5: Grün (Gesunde Beziehung)
    - 1.5-3.0: Gelb (Einige Warnsignale)
    - 3.0-4.0: Orange (Viele Red Flags)
    - 4.0-5.0: Rot (Kritische Anzahl)
    
    Usage: <div class="bg-gradient-to-r {{ analysis.score_total|score_color_class }}">
    """
    try:
        score = float(score)
    except (TypeError, ValueError):
        return "from-gray-400 to-gray-500"
    
    if score < 1.5:
        return "from-green-400 to-green-500"
    elif score < 3.0:
        return "from-yellow-400 to-yellow-500"
    elif score < 4.0:
        return "from-orange-400 to-orange-500"
    else:
        return "from-red-500 to-red-600"


@register.filter
def score_category(score):
    """
    Gibt Kategorie-Info für Score zurück (Text + Icon).
    
    Returns: Dict mit 'emoji', 'label', 'description'
    
    Usage: {% with category=analysis.score_total|score_category %}
               {{ category.emoji }} {{ category.label }}
           {% endwith %}
    """
    try:
        score = float(score)
    except (TypeError, ValueError):
        return {
            'emoji': '❓',
            'label': 'Unbekannt',
            'description': 'Score konnte nicht berechnet werden',
            'color': 'gray'
        }
    
    if score < 1.5:
        return {
            'emoji': '🟢',
            'label': 'Gesunde Beziehung',
            'description': 'Sehr wenige Red Flags - Weiter so!',
            'color': 'green'
        }
    elif score < 3.0:
        return {
            'emoji': '🟡',
            'label': 'Einige Warnsignale',
            'description': 'Aufmerksamkeit empfohlen',
            'color': 'yellow'
        }
    elif score < 4.0:
        return {
            'emoji': '🟠',
            'label': 'Viele Red Flags',
            'description': 'Vorsicht geboten',
            'color': 'orange'
        }
    else:
        return {
            'emoji': '🔴',
            'label': 'Kritische Anzahl',
            'description': 'Professionelle Hilfe erwägen',
            'color': 'red'
        }


@register.filter
def score_text_color(score):
    """
    Gibt Text-Farbklasse für Score zurück.
    Usage: <span class="{{ analysis.score_total|score_text_color }}">
    """
    try:
        score = float(score)
    except (TypeError, ValueError):
        return "text-gray-800"
    
    if score < 1.5:
        return "text-green-700"
    elif score < 3.0:
        return "text-yellow-700"
    elif score < 4.0:
        return "text-orange-700"
    else:
        return "text-red-700"
