from django import template
from django.template.defaultfilters import default


register = template.Library()


@register.filter(name="format_duration")
def format_duration(seconds):
    if seconds > 60:
        minutes, remaining_seconds = divmod(seconds, 60)
        duration = f"{minutes}m"

        if remaining_seconds == 0:
            return f"{minutes}m"
        return f"{minutes}m{default(remaining_seconds, '0')}s"

    return f"{seconds}s"

@register.filter
def format_seconds(seconds):
    m, s = divmod(seconds, 60)
    return f"{m:02d}:{s:02d}"
