from django import forms
from django.utils.translation import gettext_lazy as _

from company.models import UsersContacts
from crm.models import Contract, BoardPermissions


class ContractEditForm(forms.ModelForm):
    board_member = forms.ModelChoiceField(label=_('Board member'), required=True, empty_label=None, queryset=None, widget=forms.Select(attrs={"class": "form-control"}))

    class Meta:
        model = Contract
        exclude = ['created_at', 'status', 'company']

    def __init__(self, *args, **kwargs):
        board_members = kwargs.pop('board_members', None)
        user = kwargs.pop('user', None)

        super(ContractEditForm, self).__init__(*args, **kwargs)
        for field in self.fields.keys():
            self.fields[field].widget.attrs.update({'class': 'form-control'})

        if board_members:
            self.fields['board_member'].queryset = board_members
        self.fields['contact'].queryset = UsersContacts.objects.filter(listcontainer__list__list_owner=user)


class ContractEditFormNonOwner(forms.ModelForm):
    class Meta:
        model = Contract
        exclude = ['created_at', 'status', 'board_member', 'company']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(ContractEditFormNonOwner, self).__init__(*args, **kwargs)
        for field in self.fields.keys():
            self.fields[field].widget.attrs.update({'class': 'form-control'})
        self.fields['contact'].queryset = UsersContacts.objects.filter(listcontainer__list__list_owner=user)


class ChangeBoardRole(forms.Form):
    # Model that allows to change user role
    role = forms.ChoiceField(choices=BoardPermissions.roles[1::], widget=forms.Select(attrs={
        "class": "form-control",
        "id": "role",
    }))
    permission_id = forms.IntegerField(widget=forms.HiddenInput())

    def __init__(self, *args, **kwargs):
        if 'permission_id' in kwargs:
            permission_id = kwargs.pop('permission_id')
        else:
            permission_id = args[0].get('permission_id')
        super(ChangeBoardRole, self).__init__(*args, **kwargs)
        self.fields['permission_id'].initial = permission_id


class EditBoardName(forms.Form):
    name = forms.CharField(label=_('Input new board name'), widget=forms.TextInput(attrs={
        "class": "form-control",
        "placeholder": _("Board name"),
        "id": "name",
    }))
