from django.contrib import admin

from .models import Contract, Currency, ContractStatus, Board, BoardPermissions, BoardInvite


@admin.register(Contract)
class ContractAdmin(admin.ModelAdmin):
    pass


@admin.register(Currency)
class CurrencyAdmin(admin.ModelAdmin):
    pass


@admin.register(ContractStatus)
class ContractStatusAdmin(admin.ModelAdmin):
    pass


@admin.register(Board)
class BoardAdmin(admin.ModelAdmin):
    pass


@admin.register(BoardPermissions)
class BoardPermissionsAdmin(admin.ModelAdmin):
    pass


@admin.register(BoardInvite)
class BoardInviteAdmin(admin.ModelAdmin):
    pass
