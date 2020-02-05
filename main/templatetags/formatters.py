from django import template
from django.template.defaultfilters import stringfilter
from re import sub

register = template.Library()


@register.filter(name="phone_number")
@stringfilter
def format_phone_number(value):
    """
    Format a phone number. The number has to be at least 7 numerical digits.
    :param value: a raw character string of a phone number
    :return: nothing for invalid phone numbers, otherwise an attempt at formatting it.
    """
    value = sub("[^0-9]", "", value) # Remove all characters that aren't numerical.
    try:
        out = f"{value[-7:-4]}-{value[-4:]}"
        if len(value) >= 10:
            out = f"({value[-11:-7]}) {out}"
        if len(value) >= 12:
            out = f"+{value[-12:-11]} {out}"
        return out
    except:
        return ""


@register.filter(name="brief_description")
@stringfilter
def format_brief_description(value):
    """
    Keep a description to around 50 to 53 characters or less.
    """
    out = ""
    split = value.split(" ")
    for word in split:
        out = out + word + " "
        if len(out) >= 50:
            # Make the end of the description ellipses
            out = out[:50].strip() + "..."
            break
    return out


@register.filter(name="brief_description_120")
@stringfilter
def format_brief_description_120(value):
    """
    Keep a description to around 120 characters or less.
    """
    out = ""
    split = value.split(" ")
    for word in split:
        out = out + word + " "
        if len(out) >= 120:
            # Make the end of the description ellipses
            out = out[:120].strip() + "..."
            break
    return out


@register.filter(name="brief_description_80")
@stringfilter
def format_brief_description_80(value):
    """
    Keep a description to around 120 characters or less.
    """
    out = ""
    split = value.split(" ")
    for word in split:
        out = out + word + " "
        if len(out) >= 80:
            # Make the end of the description ellipses
            out = out[:180].strip() + "..."
            break
    return out


@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)


@register.filter
def exclude(base, value):
    return (value in base)