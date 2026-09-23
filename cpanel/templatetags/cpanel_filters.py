from django import template
from django.utils.timezone import now
from persiantools.jdatetime import JalaliDate


register = template.Library()


@register.filter(name='split_by')
def split_by(value, arg):
    if isinstance(value, str):
        return value.split(arg)
    return value


@register.filter
def to_jalali(value):
    return JalaliDate(value, locale='fa')


@register.filter
def to_jalali_c(value):
    return JalaliDate(value, locale='fa').strftime('%c')


@register.filter
def days_ago(value):
    days = (now().date() - value.date()).days
    return f'{days} روز قبل '


@register.filter
def filter_assessment_title(assessments, title):
    return [assessment for assessment in assessments if assessment['title'] == title]


@register.filter
def get_history_item(history_list, index):
    try:
        return history_list[-index]
    except (IndexError, TypeError):
        return None


@register.filter
def get_history_change(history_list):
    try:
        return round(history_list[-1] - history_list[-2], 2)
    except (IndexError, TypeError):
        return None


@register.filter(name='mul')
def mul(value, arg):
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return value
