from modeltranslation.translator import register, TranslationOptions

from .models import ContractStatus
from SalesTech.settings import MODELTRANSLATION_LANGUAGES


@register(ContractStatus)
class ContractStatusTranslationOptions(TranslationOptions):
    fields = ('name',)
    required_languages = MODELTRANSLATION_LANGUAGES