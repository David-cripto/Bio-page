from django import template
from django.utils.html import conditional_escape
from django.utils.safestring import mark_safe


register = template.Library()


@register.filter
def highlight_author(authors, author_name):
    escaped_authors = conditional_escape(authors or "")
    escaped_name = conditional_escape(author_name or "")
    if not escaped_name:
        return escaped_authors

    highlighted = escaped_authors.replace(
        escaped_name,
        f'<span class="author-highlight">{escaped_name}</span>',
    )
    return mark_safe(highlighted)
