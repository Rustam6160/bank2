from django import template

register = template.Library()

@register.simple_tag
def counter(n):
    s = 0
    for i in n:
        s += 1
    return s


@register.inclusion_tag('main/history_range.html')
def tr_history(transactions):
    return {'transactions': transactions}