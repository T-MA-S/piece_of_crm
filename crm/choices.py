from django.db import models
from django.utils.translation import gettext_lazy as _


class ContractStatusColorChoices(models.TextChoices):

    PRIMARY = 'primary', _('Blue')
    SECONDARY = 'secondary', _('Gray')
    SUCCESS = 'success', _('Green')
    DANGER = 'danger', _('Red')
    WARNING = 'warning', _('Yellow')
    INFO = 'info', _('Сyan')
    WHITE = 'white', _('White')

    
