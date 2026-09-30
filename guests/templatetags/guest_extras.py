from django import template


register = template.Library()


@register.filter
def get_item(mapping, key):
    if not isinstance(mapping, dict):
        return ""
    return mapping.get(str(key), "")
