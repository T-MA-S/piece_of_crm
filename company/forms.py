from django import forms
from django.utils.translation import gettext_lazy as _
from phonenumber_field.formfields import PhoneNumberField as PNF

from .models import *
from .utils import validate_file_extension


class AddTemplateListForm(forms.Form):
    list_name = forms.CharField(label=_("List Name"),
                                widget=forms.TextInput(attrs={"class": "form-control"}))


class TransferTemplate(forms.Form):
    def __init__(self, *args, **kwargs):
        templates_lists = kwargs.pop('templates_lists', None)
        super(TransferTemplate, self).__init__(*args, **kwargs)
        lists = [(int(template_list.pk), str(template_list.list_name))
                 for template_list in templates_lists]
        self.fields['templates_list'].choices = lists

    templates_list = forms.ChoiceField(label=_('Template List'), required=False,
                                       widget=forms.Select(attrs={
                                           "class": "form-control form-control-user",
                                       }))


class AddMessageTemplateForm(forms.Form):
    template_name = forms.CharField(label=_("Template Name"),
                                    widget=forms.TextInput(attrs={"class": "form-control"}))

    subject_line = forms.CharField(label=_("Subject line"),
                                   widget=forms.TextInput(attrs={"class": "form-control"}))


class AddNewsletterTemplatesListForm(forms.Form):
    list_name = forms.CharField(label=_("List Name"),
                                widget=forms.TextInput(attrs={"class": "form-control"}))


class TransferNewsletter(forms.Form):
    def __init__(self, *args, **kwargs):
        newsletters_lists = kwargs.pop('newsletters_lists', None)
        super(TransferNewsletter, self).__init__(*args, **kwargs)
        lists = [(int(newsletters_list.pk), str(newsletters_list.list_name))
                 for newsletters_list in newsletters_lists]
        self.fields['newsletters_list'].choices = lists

    newsletters_list = forms.ChoiceField(label=_('Newsletter templates lists'), required=False,
                                         widget=forms.Select(attrs={
                                             "class": "form-control form-control-user",
                                         }))


class SetTemplateForm(forms.Form):
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(SetTemplateForm, self).__init__(*args, **kwargs)
        templates = [(int(template.pk), str(template.template_name))
                     for template in Template.objects.filter(template_list__user=user)]
        self.fields['templates'].choices = templates

    templates = forms.ChoiceField(label=_('Template'), required=False,
                                  widget=forms.Select(attrs={
                                      "class": "form-control form-control-user",
                                  }))


class AddSendingTemplateList(forms.Form):

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(AddSendingTemplateList, self).__init__(*args, **kwargs)
        templates = [(int(template.pk), str(template.newsletter_name))
                     for template in NewsletterTemplate.objects.filter(newsletter_list__user=user)]
        self.fields['templates'].choices = templates

        users = [(int(users_list.pk), str(users_list.list_name))
                 for users_list in List.objects.filter(list_owner=user).select_related('list_owner', 'list_owner__company')]
        self.fields['users_lists'].choices = users

    list_name = forms.CharField(label=_('List Name'), widget=forms.TextInput(attrs={
        "class": "form-control form-control-user",
        "placeholder": _("List Name"),
        "id": "firstname",

    }))

    templates = forms.ChoiceField(label=_('Templates'), required=True,
                                  widget=forms.Select(attrs={
                                      "class": "form-control form-control-user",
                                  }))
    users_lists = forms.ChoiceField(label=_('Clients list'), required=True,
                                    widget=forms.Select(attrs={
                                        "class": "form-control form-control-user",
                                    }))


class AddContactForm(forms.Form):
    first_name = forms.CharField(label=_('First name'), required=False, widget=forms.TextInput(attrs={
        "class": "form-control form-control-user",
        "placeholder": _("First name"),
        "id": "firstname",

    }))
    surname = forms.CharField(label=_('Surname'), required=False, widget=forms.TextInput(attrs={
        "class": "form-control form-control-user",
        "placeholder": _("Surname"),
        "id": "surname",

    }))
    middle_name = forms.CharField(label=_('Middle Name'), required=False, widget=forms.TextInput(attrs={
        "class": "form-control form-control-user",
        "placeholder": _("Middle Name"),
        "id": "middle_name"
    }))
    email = forms.EmailField(label=_('Email'), widget=forms.EmailInput(attrs={
        "class": "form-control form-control-user",
        "placeholder": _("Email"),
        "id": "email"
    }))

    phone_number = PNF(label=_('Phone Number'), required=False, widget=forms.TextInput(attrs={
        "class": "form-control form-control-user",
        "placeholder": _('Phone Number'),
        'type': "tel",
        'data-tel-input placeholder': "Phone",
        "maxlength": "18"
    }))

    position = forms.CharField(label=_('Position'), required=False, widget=forms.TextInput(attrs={
        "class": "form-control form-control-user",
        "placeholder": _("Position"),
        "id": "position"
    }))

    # TODO: Добавить возможность вписывать свою компанию в поля company и site
    company = forms.CharField(label=_('Company name'), required=False,
                              widget=forms.TextInput(
                                  attrs={"class": "basicAutoComplete form-control form-control-user",
                                         "data-url": '/ru/company/company_name_autocomplete',
                                         "onchange": "company_field_changed(this.value)"}))

    # company_choices = list(ContactCompany.objects.values_list('id', 'company_site'))
    site = forms.CharField(label=_('Company website'), required=False, widget=forms.TextInput(attrs={"class": "form-control form-control-user"}))
    telegram_id = forms.IntegerField(label=_('Telegram Chat id'), required=False, widget=forms.NumberInput(attrs={"class": "form-control form-control-user", "placeholder": _("Unique identifier for the target chat")}))


class CreateAndAddContactFromGeneratedMail(forms.Form):

    def __init__(self, *args, **kwargs):
        _user_lists = kwargs.pop('user_lists')
        super(CreateAndAddContactFromGeneratedMail,
              self).__init__(*args, **kwargs)
        self.fields['user_lists'].choices = _user_lists

    user_lists = forms.CharField(
        label=_("User Lists"), widget=forms.Select(attrs={"class": "id_user_lists"}))

    first_name = forms.CharField(label=_('First name'), required=False, widget=forms.TextInput(attrs={
        "class": "form-control form-control-user",
        "placeholder": _("First name"),
        "id": "firstname",

    }))
    surname = forms.CharField(label=_('Surname'), required=False, widget=forms.TextInput(attrs={
        "class": "form-control form-control-user",
        "placeholder": _("Surname"),
        "id": "surname",

    }))
    middle_name = forms.CharField(label=_('Middle Name'), required=False, widget=forms.TextInput(attrs={
        "class": "form-control form-control-user",
        "placeholder": _("Middle Name"),
        "id": "middle_name"
    }))
    email = forms.EmailField(label=_('Email'), widget=forms.EmailInput(attrs={
        "class": "form-control form-control-user",
        "placeholder": _("Email"),
        "id": "email"
    }))

    phone_number = forms.CharField(label=_('Phone Number'), required=False, widget=forms.TextInput(attrs={
        "class": "form-control form-control-user",
        "placeholder": _('Phone Number'),
        'type': "tel",
        'data-tel-input placeholder': "Phone",
        "maxlength": "18"
    }))

    position = forms.CharField(label=_('Position'), required=False, widget=forms.TextInput(attrs={
        "class": "form-control form-control-user",
        "placeholder": _("Position"),
        "id": "position"
    }))

    # TODO: Добавить возможность вписывать свою компанию в поля company и site
    company = forms.CharField(label=_('Company name'), required=False,
                              widget=forms.TextInput(
                                  attrs={"class": "basicAutoComplete form-control form-control-user",
                                         "data-url": '/ru/company/company_name_autocomplete',
                                         "onchange": "company_field_changed(this.value)"}))

    # company_choices = list(ContactCompany.objects.values_list('id', 'company_site'))
    site = forms.CharField(label=_('Company website'), required=False,
                           widget=forms.TextInput(attrs={"class": "form-control form-control-user"}))


class AddContactsFromFileForm(forms.Form):
    file = forms.FileField(label=_('File'), required=True,
                           validators=[validate_file_extension], widget=forms.FileInput(attrs={"class": "form-control", "accept": ".csv"}))


class TransferContact(forms.Form):
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(TransferContact, self).__init__(*args, **kwargs)
        lists = [(int(list.pk), str(list.list_name))
                 for list in List.objects.filter(list_owner=user).select_related('list_owner', 'list_owner__company')]
        self.fields['contacts_list'].choices = lists

    contacts_list = forms.ChoiceField(label=_('Client List'), required=False,
                                      widget=forms.Select(attrs={
                                          "class": "form-control form-control-user",
                                      }))


class RenameList(forms.Form):
    name_list = forms.CharField(label=_("Name of the list"))


class AddList(forms.Form):
    list_name = forms.CharField(label=_("Name of the list"),
                                widget=forms.TextInput(attrs={"class": "form-control"}))


class FindContactByName(forms.Form):
    name = forms.CharField(label=_('Name'),
                           widget=forms.TextInput(attrs={
                               "class": "form-control form-control-user",
                               "placeholder": _("First name"),
                               "pattern": "[A-Za-zА-Яа-яЁё\s-]{2,}",
                               "title": _("You can use only latin and cyrillic symbols")
                           }))

    surname = forms.CharField(label=_('Surname'),
                              widget=forms.TextInput(attrs={
                                  "class": "form-control form-control-user",
                                  "placeholder": _("Surname"),
                                  "pattern": "[A-Za-zА-Яа-яЁё-]{2,}",
                                  "title": _("You can use only latin and cyrillic symbols")
                              }))

    domain = forms.CharField(label=_('Domain'), required=True,
                             widget=forms.TextInput(attrs={
                                 "id": "domain_company",
                                 "class": "form-control form-control-user",
                                 "placeholder": "example.com",
                                 "pattern": "(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z0-9][a-z0-9-]{0,61}[a-z0-9]",
                                 "title": _("The entered domain is not correct")
                             }))


class FindContactByDomain(forms.Form):
    domain = forms.CharField(label=_('Domain'), required=True,
                             widget=forms.TextInput(attrs={
                                 "id": "domain_company",
                                 "class": "form-control form-control-user",
                                 "placeholder": "example.com",
                                 "pattern": "(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z0-9][a-z0-9-]{0,61}[a-z0-9]",
                                 "title": _("The entered domain is not correct")
                             }))


class FindContactByFeature(forms.Form):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        sizes = [(size.size, str(size.size))
                 for size in CompanySizes.objects.all()]
        branches = [(branch.industry_ru, str(branch.industry))
                    for branch in CompanyBranch.objects.all().order_by('industry')]
        sizes.insert(0, (None, None))
        branches.insert(0, (None, None))
        self.fields['company_size'].choices = sizes
        self.fields['company_branch'].choices = branches

    company_size = forms.ChoiceField(label=_('Size'), required=False,
                                     widget=forms.Select(attrs={
                                         "class": "form-control form-control-user",
                                     }))

    company_branch = forms.ChoiceField(label=_('Industry'), required=False,
                                       widget=forms.Select(attrs={
                                           "class": "form-control form-control-user",
                                       }))


class AddContactToExistingList(forms.Form):
    user_lists = forms.ModelChoiceField(
        queryset=None, to_field_name='list_name')

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request')
        super().__init__(*args, **kwargs)
        self.fields['user_lists'].queryset = List.objects.filter(
            list_owner__id=self.request.user.id).select_related('list_owner', 'list_owner__company')


class OperatorBranchSearch(forms.Form):

    def __init__(self, *args, **kwargs):
        super(OperatorBranchSearch, self).__init__(*args, **kwargs)
        branches = [(branch.pk, branch.industry)
                    for branch in CompanyBranch.objects.all()]
        self.fields['industry'].choices = branches

        sizes = [(size.pk, size.size) for size in CompanySizes.objects.all()]
        self.fields['company_size'].choices = sizes

    industry = forms.CharField(label=_('Industry'),
                               required=False,
                               widget=forms.Select(attrs={
                                   "class": "form-control form-control-user",
                                   "placeholder": _("Industry"),

                               }))

    company_size = forms.CharField(label=_('Size'),
                                   required=False,
                                   widget=forms.Select(attrs={
                                       "class": "form-control form-control-user",
                                       "placeholder": _("Size"),
                                   }))
