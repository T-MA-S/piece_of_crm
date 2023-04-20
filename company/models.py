import uuid

import django.utils.timezone
from django.db import models
from phonenumber_field.modelfields import PhoneNumberField
from django.utils.translation import gettext_lazy as _

from users.models import UserModel


class TemplatesList(models.Model):

    user = models.ForeignKey(UserModel, on_delete=models.CASCADE)
    list_name = models.CharField('List Name', max_length=128)

    def __str__(self):
        return str(self.list_name)


class Template(models.Model):
    template_list = models.ForeignKey(TemplatesList, on_delete=models.CASCADE, null=True)
    template_name = models.CharField('Template Name', max_length=128, null=True)
    subject_line = models.CharField('Subject line', max_length=128)
    message = models.TextField('Message')

    def __str__(self):
        return str(self.template_name)

    class Meta:
        ordering = ('-id',)


class UserLocalVariable(models.Model):
    name = models.CharField('Название', max_length=128)
    variable = models.CharField('Переменная', max_length=128)

    def __str__(self):
        return str(self.name)


class NewsletterTemplatesList(models.Model):
    user = models.ForeignKey(UserModel, on_delete=models.CASCADE)
    list_name = models.CharField('List Name', max_length=128)

    def __str__(self):
        return str(self.list_name)


class NewsletterTemplate(models.Model):
    newsletter_list = models.ForeignKey(NewsletterTemplatesList, verbose_name='Newsletter List',
                                        on_delete=models.CASCADE)
    newsletter_name = models.CharField('Название рассылки', max_length=128)
    sequence = models.TextField('Sequence', null=True)
    visual = models.TextField('Visual')  # данные для подстановки при редактировании
    data = models.TextField('Data')
    pop_up_data = models.TextField('PopUps Data')  # данные для подстановки при редактировании в pop-up'ы

    def __str__(self):
        return str(self.newsletter_name)

    class Meta:
        ordering = ('-id',)


class CompanySizes(models.Model):
    size = models.CharField('Размер', max_length=128)

    def __str__(self):
        return self.size

    class Meta:
        verbose_name = 'Размер'
        verbose_name_plural = 'Размеры'


class CompanyBranch(models.Model):
    industry = models.CharField('Индустрия', max_length=255)

    def __str__(self):
        return self.industry

    class Meta:
        verbose_name = 'Индустрия'
        verbose_name_plural = 'Индустрии'


class ContactCompany(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    company_name = models.CharField("Название компании", max_length=128)
    company_site = models.URLField("Сайт компании", max_length=128)
    company_branch = models.ForeignKey(CompanyBranch, on_delete=models.DO_NOTHING, null=True, default=None)
    company_size = models.ForeignKey(CompanySizes, on_delete=models.DO_NOTHING, null=True, default=None)
    location = models.TextField('Локация', null=True, default=None)
    phone_number = models.CharField('Номер телефона', max_length=18, null=True, default=None)
    description = models.TextField('Описание', null=True, default=None)

    apollo_hash = models.TextField('hash', null=True,
                                   default=None)  # временное поле для хранения хэша и соотношения с хэшем пользователя

    def __str__(self):
        return f'{self.company_name} ({self.company_site})'

    class Meta:
        ordering = ('-id',)
        verbose_name = 'Компания контакта'
        verbose_name_plural = 'Компании контактов'


class AbstractContact(models.Model):
    class Meta:
        abstract = True

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    name = models.CharField("Имя", max_length=128, null=True)
    surname = models.CharField("Фамилия", max_length=128, null=True)
    middle_name = models.CharField("Отчество", max_length=128, null=True)
    email = models.EmailField("Email", max_length=128)
    phone = PhoneNumberField("Номер телефона", null=True)

    company = models.ForeignKey(ContactCompany, on_delete=models.SET_NULL, null=True)
    position_in_company = models.CharField("Позиция в компании", max_length=128, null=True)

    linkedin_link = models.TextField('LinkedIn', null=True)
    telegram_id = models.CharField(max_length=128, null=True, default=None)

    def __str__(self):
        return f"{self.surname} {self.name} {self.middle_name} ({self.email})"
    
    @property
    def full_name(self):
        return f"{self.surname if self.surname else ''} {self.name if self.name else ''} {self.middle_name if self.middle_name else ''}".strip()


class Contact(AbstractContact):

    @classmethod
    def create_with_company_name(cls, name: str, surname: str, middle_name: str, email: str, phone: str,
                                 company_name_to_find: str, position_in_company: str):
        """
        Метод создающий инстанс контакта с указанием названия компании, а с передачей инстанса самой компании
        :param company_name_to_find:
        :return: Contact - созданный инстанс контакта
        """

        company = ContactCompany.objects.get(company_name=company_name_to_find)

        instance = cls(name=name, surname=surname, middle_name=middle_name, email=email, phone=phone,
                       position_in_company=position_in_company)
        instance.company = company
        return instance

    class Meta:
        ordering = ('-id',)
        verbose_name = 'Контакт (наш, т.е внутренний, не созданный пользователем)'
        verbose_name_plural = 'Контакт (наши, т.е внутренние)'


class UsersContacts(AbstractContact):
    class Meta:
        verbose_name = 'Контакт созданный пользователем'
        verbose_name_plural = 'Контакты созданные пользователями'

    @classmethod
    def create_user_contact_from_contact(cls, contact: Contact):
        instance = cls(name=contact.name, surname=contact.surname, middle_name=contact.middle_name,
                       email=contact.email, phone=contact.phone, position_in_company=contact.position_in_company)
        instance.save()
        instance.company = contact.company
        return instance

    class Meta:
        ordering = ('-id',)


class List(models.Model):
    list_name = models.CharField("Имя списка", max_length=128)
    list_owner = models.ForeignKey(UserModel, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.list_name}'

    class Meta:
        ordering = ('-id',)
        verbose_name = 'Список'
        verbose_name_plural = 'Списки'


class ListContainer(models.Model):
    list = models.ForeignKey(List, on_delete=models.CASCADE)  # type: ignore
    contact = models.ForeignKey(UsersContacts, on_delete=models.CASCADE, null=True)  # type: ignore

    def __str__(self):
        return f"ListContainer(List={self.list.list_name}(id={self.list.id}), Contact={self.contact}, id={self.id})"

    class Meta:
        ordering = ('-id',)


class RequestsForSearch(models.Model):
    name = models.CharField("Имя (Кириллица)", max_length=128, null=True)
    surname = models.CharField("Фамилия (Кириллица)", max_length=128, null=True)
    name_lat = models.CharField("Имя (Латиница)", max_length=128, null=True)
    surname_lat = models.CharField("Фамилия (Латиница)", max_length=128, null=True)
    company_domain = models.CharField("Домен", max_length=30, null=True)

    def __str__(self):
        return f'{self.name} - {self.surname}'

    class Meta:
        ordering = ('-id',)
        verbose_name = 'Запрос с поиска'
        verbose_name_plural = 'Запросы с поиска'


class FindEmails(models.Model):
    VALID = 'VALID'
    PROBABLY = 'PROBABLY'
    INVALID = 'INVALID'

    email_statuses = [
        (VALID, _('Valid')),
        (PROBABLY, _('Probably valid')),
        (INVALID, _('Invalid'))
    ]

    email = models.EmailField('Найденный имейл', max_length=128)
    request_for_search = models.ForeignKey(RequestsForSearch, on_delete=models.CASCADE)
    status = models.CharField(max_length=10, choices=email_statuses, default='VALID')

    def __str__(self):
        return f'{self.email}'

    class Meta:
        ordering = ('-id',)
        verbose_name = 'Найденная почта'
        verbose_name_plural = 'Найденные почты'


class Notification(models.Model):
    UNREAD = 'UNREAD'
    READ = 'READ'
    DELETED = 'DELETED'
    statuses = [
        (UNREAD, 'Unread'),
        (READ, 'Read'),
        (DELETED, 'Deleted')
    ]
    receiver = models.ForeignKey(UserModel, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=statuses, default=UNREAD)
    text = models.CharField(max_length=10000)
    created_at = models.DateTimeField(default=django.utils.timezone.now)
    redirect_url = models.URLField(max_length=255, null=True, default=None)

    def __str__(self):
        return f'{self.receiver} - {self.status}'

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Уведомление'
        verbose_name_plural = 'Уведомления'


class SendingMailsList(models.Model):
    list_name = models.CharField('Название листа', max_length=128)
    newsletter = models.ForeignKey(NewsletterTemplate, on_delete=models.SET_NULL, null=True)
    owner = models.ForeignKey(UserModel, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return f'{self.list_name}'

    class Meta:
        verbose_name = 'Список рассылок'
        verbose_name_plural = 'Списки рассылок'


class SendingAbstrat(models.Model):
    statuses = [(1, _("Pending")),
                (2, _("Delivered")),
                (3, _("Error")),
                (4, _("Opened")),
                (5, _("Cancelled"))]

    sendingmails_list = models.ForeignKey(SendingMailsList, on_delete=models.CASCADE)
    message = models.TextField('Message')
    theme = models.CharField('Theme', max_length=2000)
    recipient = models.ForeignKey(UsersContacts, verbose_name='Recipient', on_delete=models.CASCADE)
    status = models.CharField('Status', max_length=128, choices=statuses)
    date = models.DateTimeField()
    active = models.BooleanField('Active')
    template_name = models.TextField(null=True)
    error_description = models.TextField('error_description', null=True)

    class Meta:
        abstract = True

    @property
    def is_email(self):
        return hasattr(self, 'link')


class SendingMails(SendingAbstrat):

    link = models.CharField('Recipient', max_length=2000)
    opened_at = models.DateTimeField(null=True)
    conditions = models.TextField('conditions', null=True)
    opened_at_visual = models.TextField('opened_at_visual', null=True)

    def __str__(self):
        return f'{self.theme}'

    class Meta:
        ordering = ('-id',)
        verbose_name = 'Письмо для отправки (Email)'
        verbose_name_plural = 'Письма для отправки (Email)'


class SendingTelegram(SendingAbstrat):

    def __str__(self):
        return f'{self.theme}'

    class Meta:
        ordering = ('-id',)
        verbose_name = 'Письмо для отправки (Telegram)'
        verbose_name_plural = 'Письма для отправки (Telegram)'