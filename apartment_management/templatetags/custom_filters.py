from django import template
register = template.Library()

@register.filter
def range_custom(start, end):
    return range(start, end + 1)

@register.simple_tag
def querystring(request, **kwargs):
    """Tái tạo query string giữ lại các param cũ, thay thế bằng param mới nếu có."""
    updated = request.GET.copy()
    for key, value in kwargs.items():
        updated[key] = value
    return updated.urlencode()