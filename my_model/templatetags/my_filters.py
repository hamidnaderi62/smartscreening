from django import template
register = template.Library()

@register.filter(name='split_by')
def split_by(value, arg):
    """Splits a string by the specified delimiter."""
    if isinstance(value, str):
        return value.split(arg)
    return value



from persiantools.jdatetime import JalaliDate
from django.utils.timezone import now
@register.filter
def to_jalali(value):
    return JalaliDate(value, locale="fa")

@register.filter
def to_jalali_c(value):
    return JalaliDate(value, locale="fa").strftime('%c')


@register.filter
def days_ago(value):
    days = (now().date() - value.date()).days
    return  (f'{days} روز قبل ')

@register.filter
def filter_assessment_title(assessments, title):
    return [a for a in assessments if a['title'] == title]


@register.filter
def get_history_item(history_list,idx):
    try:
        return history_list[-idx]
    except (IndexError, TypeError):
        return None


@register.filter
def get_history_change(history_list):
    try:
        return history_list[-1]-history_list[-2]
    except (IndexError, TypeError):
        return None