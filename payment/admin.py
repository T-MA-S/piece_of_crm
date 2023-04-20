from django.contrib import admin

from .models import RobokassaTransaction, PromoCode


@admin.register(RobokassaTransaction)
class RobokassaTransactionAdmin(admin.ModelAdmin):
    readonly_fields = ('plan', 'user', 'price', 'description', 'created_time', 'payed_time', 'canceled_time', 'hash')

@admin.register(PromoCode)
class PromoCodeAdmin(admin.ModelAdmin):
    pass