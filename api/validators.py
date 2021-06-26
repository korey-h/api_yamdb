import datetime as dt

from django.core.exceptions import ValidationError


def validate_year(value):
    current_year = dt.date.today().year
    if value == 0 or value > current_year:
        raise ValidationError('Wrong year')
