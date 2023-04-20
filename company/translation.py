from modeltranslation.translator import register, TranslationOptions

from .models import CompanyBranch, UserLocalVariable, Notification
from SalesTech.settings import MODELTRANSLATION_LANGUAGES


@register(CompanyBranch)
class CompanyBranchTranslationOptions(TranslationOptions):
    fields = ('industry',)
    required_languages = MODELTRANSLATION_LANGUAGES


@register(UserLocalVariable)
class UserLocalVariableTranslationOptions(TranslationOptions):
    fields = ('name',)
    required_languages = MODELTRANSLATION_LANGUAGES


@register(Notification)
class NotificationTranslationOptions(TranslationOptions):
    fields = ('text',)
    required_languages = MODELTRANSLATION_LANGUAGES