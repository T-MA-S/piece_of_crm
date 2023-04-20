import json

from django import template

from company.models import UserLocalVariable, SendingAbstrat, List
from dashboard.models import ApplicationSettings

register = template.Library()


@register.simple_tag(name='update')
def update_template_variable(value):
    return value


@register.simple_tag(name='get_user_contats_lists')
def get_user_contats_lists(user):
    return List.objects.filter(list_owner=user)


@register.simple_tag(name='updated_value')
def get_updated_value(value): return value


@register.simple_tag(name='get_variables')
def get_variables():
    variables = [{"id": variable.pk, "name": variable.name, "variable": variable.variable} for variable in UserLocalVariable.objects.all()]
    return variables, json.dumps(variables)


@register.simple_tag(name='get_validator_is_active')
def validator_is_active():
    return ApplicationSettings.objects.first().is_validator_active

@register.simple_tag(name='get_sending_statuses')
def get_sending_statuses():
    return SendingAbstrat.statuses
