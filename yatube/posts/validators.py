from django import forms


def validate_empty_field(value):
    if value == '':
        raise forms.ValidationError()
