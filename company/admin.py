from django.contrib import admin
from .models import *


@admin.register(CompanyBranch)
class CompanyBranchAdmin(admin.ModelAdmin):
    fields = ('industry_ru', 'industry_en')
    list_display = ('id', 'industry')
    list_display_links = ('industry',)


@admin.register(CompanySizes)
class CompanySizesAdmin(admin.ModelAdmin):
    list_display = ('id', 'size')
    list_display_links = ('size',)


@admin.register(ContactCompany)
class ContactCompanyAdmin(admin.ModelAdmin):
    list_display = ('id', 'company_name')
    list_display_links = ('company_name',)
    readonly_fields = ('id',)


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ('id', 'email', 'company')
    list_display_links = ('email',)
    readonly_fields = ('id',)


@admin.register(List)
class ListAdmin(admin.ModelAdmin):
    list_display = ('id', 'list_name')
    list_display_links = ('list_name',)


@admin.register(ListContainer)
class ListContainerAdmin(admin.ModelAdmin):
    list_display = ('id', 'list')
    list_display_links = ('list',)


@admin.register(RequestsForSearch)
class RequestsForSearchAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'surname')
    list_display_links = ('name',)


@admin.register(FindEmails)
class FindEmailsAdmin(admin.ModelAdmin):
    list_display = ('id', 'email')
    list_display_links = ('email',)


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('id', 'receiver', 'status')
    list_display_links = ('receiver',)


admin.site.register(SendingMails)
admin.site.register(SendingTelegram)
admin.site.register(SendingMailsList)
admin.site.register(NewsletterTemplate)
admin.site.register(NewsletterTemplatesList)
admin.site.register(UsersContacts)
