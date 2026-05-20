import re

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

    pattern = re.compile(rf"{re.escape(str(escaped_name))}\*?")

    def replace_author(match):
        return f'<span class="author-highlight">{match.group(0)}</span>'

    highlighted = pattern.sub(replace_author, str(escaped_authors))
    return mark_safe(highlighted)
