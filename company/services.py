import pytz, json, logging
from datetime import timedelta, datetime
from transliterate import translit

from django.http import HttpRequest, JsonResponse
from django.urls import reverse
from django.contrib import messages
from django.db import transaction
from django.db.models import Q, F, QuerySet
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.translation import gettext_lazy, activate as activate_language

from .models import List, ListContainer, ContactCompany, Contact, UsersContacts, FindEmails, RequestsForSearch, TemplatesList, Template, NewsletterTemplatesList, NewsletterTemplate, SendingMailsList, SendingAbstrat, SendingMails, SendingTelegram
from .forms import AddContactForm, AddContactsFromFileForm, TransferContact, TransferNewsletter, AddMessageTemplateForm, TransferTemplate, SetTemplateForm, AddSendingTemplateList, FindContactByName, FindContactByDomain, FindContactByFeature, CreateAndAddContactFromGeneratedMail
from .utils import search_credit_count_limited, search_credit_count_down, get_emails_new, get_pattern_number_by_email, get_email_by_pattern_nums, handle_uploaded_csv, get_list_data, create_mails_for_user, parse_email_to_sequence
from .pagination import get_paginated_queryset

from dashboard.models import UserSettings, EmailSettings, TelegramBot
from users.models import UserModel

from users.utils import get_client_ip


logger = logging.getLogger('user_events')


def return_default_contacts_context(request: HttpRequest, list_id: int | None = None):
    user, page = request.user, request.GET.get('page', 1)
    user_lists = user.list_set.get_queryset()
    list_id_to_contacts = {_list_id: get_paginated_queryset(ListContainer.objects.filter(list__id=_list_id).select_related('list', 'contact'), page) for _list_id in user_lists.values_list("id", flat=True)}
        
    add_contacts_from_file_form = AddContactsFromFileForm()
    transfer_contact_form = TransferContact(user=user)

    context = {
        'lists': user_lists,
        'selected_list_id': list_id,
        'add_contacts_from_file_form': add_contacts_from_file_form,
        'list_id_to_contacts': list_id_to_contacts,
        'transfer_contact_form': transfer_contact_form,
        'has_no_credits': request.GET.get('has_no_credits')
    }
    return context


def return_default_templates_context(request: HttpRequest, list_id: int | None = None):
    user, page = request.user, request.GET.get('page', 1)

    templates_lists = TemplatesList.objects.filter(user=user).select_related('user')

    list_ids = {list_id: get_paginated_queryset(Template.objects.filter(
        template_list_id=list_id).select_related('template_list'), page=page) for list_id in
                templates_lists.values_list("id", flat=True)}

    add_template_form = AddMessageTemplateForm()
    transfer_template_form = TransferTemplate(templates_lists=templates_lists)

    context = {
        'selected_list_id': list_id,
        'list_ids': list_ids,
        'templates_lists': templates_lists,
        'add_template_form': add_template_form,
        'transfer_template_form': transfer_template_form
    }
    return context


def return_default_newsletters_context(request: HttpRequest, list_id: int | None = None):
    user, page = request.user, request.GET.get('page', 1)

    newsletters_lists = NewsletterTemplatesList.objects.filter(
        user=user).select_related('user')

    list_ids = {newsletters_list.pk: get_paginated_queryset(NewsletterTemplate.objects.filter(
        newsletter_list=newsletters_list).select_related('newsletter_list'), page=page) for newsletters_list in
                newsletters_lists}

    transfer_newsletter_form = TransferNewsletter(newsletters_lists=newsletters_lists)
    context = {
        'selected_list_id': list_id,
        'newsletters_lists': newsletters_lists,
        'list_ids': list_ids,
        'transfer_newsletter_form': transfer_newsletter_form
    }
    return context


def return_default_sendings_context(request: HttpRequest, list_id: int | None = None):
    user, page = request.user, request.GET.get('page', 1)
    sending_mails_lists = SendingMailsList.objects.filter(owner=user)
    list_ids = get_list_data(sending_mails_lists.values_list('id', flat=True), page)
    add_list_form = AddSendingTemplateList(user=user)
    user_settings, created = UserSettings.objects.get_or_create(user=user,defaults={'user': user})

    user_have_valid_using_smtp = EmailSettings.objects.filter(is_valid_smtp=True, is_using=True, user_settings_list=user_settings).exists()
    telegram_bots_exists = TelegramBot.objects.filter(user=user).exists()

    context = {
        'selected_list_id': list_id,
        'sending_mails_lists': sending_mails_lists,
        'list_ids': list_ids,
        'add_list_form': add_list_form,
        'user_have_valid_using_smtp': user_have_valid_using_smtp,
        'telegram_bots_exists': telegram_bots_exists
    }
    return context


def create_contacts_list(request: HttpRequest):
    user, data = request.user, json.loads(request.body.decode('utf-8'))

    list_name = data.get('list_name')
    new_list = List.objects.create(list_name=list_name, list_owner=user)

    logger.info(f'SUCCESS NEW CLIENTS LIST id="{new_list.pk}"', extra={
        'user_ip': get_client_ip(request), 'user_email': user.email})
    
    context = return_default_contacts_context(request, new_list.pk)
    return render(request, 'company/includes/contacts/contacts_lists.html', context=context)


def update_contacts_list(request):
    user, data = request.user, json.loads(request.body.decode('utf-8'))
    list_id, name_list = data.get('list_id'), data.get('name_list')

    current_list = List.objects.get(pk=list_id)
    current_list_list_name = current_list.list_name
    current_list.list_name = name_list
    current_list.save()

    logger.info(
        f'SUCCESS RENAME ("{current_list_list_name}" -> "{current_list.list_name}") CLIENTS LIST id="{current_list.pk}"',
        extra={
            'user_ip': get_client_ip(request), 'user_email': user.email})

    context = return_default_contacts_context(request, current_list.pk)
    return render(request, 'company/includes/contacts/contacts_lists.html', context=context)


def delete_contacts_list(request: HttpRequest):
    data = json.loads(request.body.decode('utf-8'))
    list_id = data.get('list_id')

    list_to_delete = List.objects.get(id=list_id)
    contacts = UsersContacts.objects.filter(listcontainer__list=list_to_delete)

    contacts.delete()
    list_to_delete.delete()

    context = return_default_contacts_context(request)
    return render(request, 'company/includes/contacts/contacts_lists.html', context=context)


def get_contacts(request: HttpRequest, list_id: int | None):
    context = return_default_contacts_context(request, list_id)
    return render(request, 'company/home.html', context)


def get_contacts_table(request: HttpRequest, list_id: int):
    user, page = request.user, request.GET.get('page', 1)
    paginator = get_paginated_queryset(ListContainer.objects.filter(list__id=list_id).select_related('list', 'contact'), page)
        
    transfer_contact_form = TransferContact(user=user)

    context = {
        'list_id': list_id,
        'paginator': paginator,
        'transfer_contact_form': transfer_contact_form
    }
    return render(request, 'company/includes/contacts/contacts_table.html', context=context)


def get_contact_email(request):
    data = json.loads(request.body.decode('utf-8'))

    if search_credit_count_limited(request.user.id):
        return JsonResponse({'error': 'Not enough credits'})

    if not (contact_id := data.get('contact_id')):
        return JsonResponse({'error': 'Not contact id'})

    contact: Contact = Contact.objects.get(pk=contact_id)

    search_credit_count_down(request.user.id)

    return JsonResponse({'email': contact.email})


def create_contact(request: HttpRequest, list_id: int):
    user = request.user

    if 'file' in request.FILES.keys():
        uploaded_file_form = AddContactsFromFileForm(
            request.POST, request.FILES)

        if uploaded_file_form.is_valid():
            try:
                with transaction.atomic():
                    result, contacts = handle_uploaded_csv(request.FILES['file'], user, list_id=list_id, is_user_contacts=True)

                    if not result and contacts == 'dialect_error':
                        messages.add_message(request, messages.ERROR, gettext_lazy(
                            'Error! The file must contain one of the delimiters: ";" or ","'))
                    elif contacts:
                        messages.add_message(request, messages.SUCCESS,
                                            gettext_lazy('Added ') + str(contacts) + gettext_lazy(' contacts'))

            except Exception as e:
                messages.add_message(request, messages.ERROR, gettext_lazy(
                    'Please enter a valid file'))
        else:
            messages.error(
                request,
                gettext_lazy('Invalid file!'))
            
        return redirect(f"{reverse('contacts_list')}?chlist={list_id}")

    elif 'first_name' in (data := json.loads(request.body.decode('utf-8'))).keys():
        context = return_default_contacts_context(request, list_id)

        if not (email := data.get('email')):
            messages.error(request, gettext_lazy('Email required field'))
            return render(request, 'company/includes/contacts/contacts_lists.html', context=context)
        
        with transaction.atomic():
            company_for_contact, created = ContactCompany.objects.get_or_create(company_name__iexact=data.get('company'), company_site__iexact=data.get('site'), defaults={'company_name': data.get('company'), 'company_site': data.get('site')})

            if company_for_contact.company_name == "":  # если имя компании не задано при создании
                company_for_contact.company_name = data.get('company')

            contacts_list: List = List.objects.get(pk=list_id)

            contact_fields = {
                'name': data.get('first_name'),
                'surname': data.get('surname'),
                'middle_name': data.get('middle_name'),
                'phone': data.get('phone_number'),
                'position_in_company': data.get('position'),
                'email': email,
                'telegram_id': data.get('telegram_id'),
                'company': company_for_contact
            }

            contact: UsersContacts = UsersContacts.objects.create(**contact_fields)

            ListContainer.objects.create(list=contacts_list, contact=contact)

            logger.info('SUCCESS ADD CLIENT', extra={'user_ip': get_client_ip(request), 'user_email': user.email})
            
    context = return_default_contacts_context(request, list_id)
    return render(request, 'company/includes/contacts/contacts_lists.html', context=context)


def edit_contact(request: HttpRequest, list_id: int):
    data = json.loads(request.body.decode('utf-8'))
    contact = UsersContacts.objects.filter(pk=data.get('contact_id'))

    context = return_default_contacts_context(request, list_id)

    if not (email := data.get('email')):
        messages.error(request, gettext_lazy('Email required field'))
        return render(request, 'company/includes/contacts/contacts_lists.html', context=context)
    
    with transaction.atomic():
        company_for_contact, created = ContactCompany.objects.get_or_create(company_site__iexact=data.get('site'), company_name__iexact=data.get('company'), defaults={'company_name': data.get('company'), 'company_site': data.get('site')})

        contact_fields = {
            'name': data.get('first_name'),
            'surname': data.get('surname'),
            'middle_name': data.get('middle_name'),
            'phone': data.get('phone_number'),
            'position_in_company': data.get('position'),
            'email': email,
            'telegram_id': data.get('telegram_id'),
            'company': company_for_contact
        }
        contact.update(**contact_fields)

        context = return_default_contacts_context(request, list_id)
        return render(request, 'company/includes/contacts/contacts_lists.html', context=context)


def transfer_contact(request: HttpRequest, list_id: int):
    data = json.loads(request.body.decode('utf-8'))
    container_id = data.get('container_id')
    ListContainer.objects.filter(pk=container_id).update(list=data.get('new_list_id'))
    context = return_default_contacts_context(request, list_id)
    return render(request, 'company/includes/contacts/contacts_lists.html', context=context)


def delete_contact(request: HttpRequest):
    data = json.loads(request.body.decode('utf-8'))
    container_id, contact_id = int(data.get('container_id')), data.get('contact_id')

    UsersContacts.objects.filter(pk=contact_id).delete()
    ListContainer.objects.filter(pk=container_id).delete()
    
    context = return_default_contacts_context(request)
    return render(request, 'company/includes/contacts/contacts_lists.html', context=context)



def contact_search(request: HttpRequest):
    user, data = request.user, json.loads(request.body.decode('utf-8'))
    list_id = int(data.get('list_id'))

    if not list_id:
        messages.error(request, gettext_lazy('Invalid request data'))
        return redirect('contacts_list')

    if not ((_list := List.objects.filter(pk=list_id)).exists() and _list.first().list_owner == user):
        messages.error(request, gettext_lazy('List not found'))
        return redirect('contacts_list')
    
    filters_data = {
        'list_id': list_id,
    }
    if name := data.get('search_name'): filters_data['contact__name__icontains'] = name
    if surname := data.get('search_surname'): filters_data['contact__surname__icontains'] = surname
    if domain := data.get('search_domain'): filters_data['contact__company__company_site__iexact'] = domain

    searched_containers = ListContainer.objects.filter(**filters_data)

    if not searched_containers: messages.error(request, gettext_lazy('Contacts not found'))

    user_lists = user.list_set.get_queryset()
    list_id_to_contacts = {_list_id: get_paginated_queryset(
        ListContainer.objects.filter(list__id=_list_id).select_related('list', 'contact') if _list_id != list_id else searched_containers) for _list_id in
        user_lists.values_list("id", flat=True)}

    add_contact_form = AddContactForm()
    add_contacts_from_file_form = AddContactsFromFileForm()
    transfer_contact_form = TransferContact(user=user)

    return render(request, 'company/includes/contacts/contacts_lists.html', context={
        'lists': user_lists,
        'list_id_to_contacts': list_id_to_contacts,
        'add_contact_form': add_contact_form,
        'add_contacts_from_file_form': add_contacts_from_file_form,
        'transfer_contact_form': transfer_contact_form
    })


def contacts_actions(request: HttpRequest):
    
    data = json.loads(request.body.decode('utf-8'))
    list_id, containers_ids, trans_id, action = data.get('list_id'), list(map(int, data.get('containers_ids'))), data.get('trans_id'), data.get('action')
    containers = ListContainer.objects.filter(pk__in=containers_ids).filter(list__list_owner=request.user, list_id=list_id)

    if action == 'del': containers.delete()
    elif action == 'trans': containers.update(list_id=trans_id)

    context = return_default_contacts_context(request)
    return render(request, 'company/includes/contacts/contacts_lists.html', context=context)


def get_templates(request: HttpRequest, list_id: int | None = None):
    context = return_default_templates_context(request, list_id)
    return render(request, 'company/templates.html', context=context)


def add_templates_list(request: HttpRequest):
    user, data = request.user, json.loads(request.body.decode('utf-8'))
    list_name = data.get('list_name')

    template_list = TemplatesList.objects.create(list_name=list_name, user=user)

    logger.info(f'SUCCESS ADD TEMPLATES LIST id="{template_list.pk}"', extra={'user_ip': get_client_ip(request), 'user_email': request.user.email})
    
    context = return_default_templates_context(request, template_list.pk)
    return render(request, 'company/includes/templates/templates_lists.html', context=context)


def edit_templates_list(request: HttpRequest):
    user, data = request.user, json.loads(request.body.decode('utf-8'))
    list_name = data.get('name_list')
    TemplatesList.objects.filter(pk=data.get('list_id'), user=user).update(list_name=list_name)

    context = return_default_templates_context(request)
    return render(request, 'company/includes/templates/templates_lists.html', context=context)


def delete_templates_list(request: HttpRequest):
    user, data = request.user, json.loads(request.body.decode('utf-8'))
    TemplatesList.objects.filter(pk=data.get('list_id'), user=user).delete()

    logger.info(f"SUCCESS DELETE TEMPLATES LIST id={data.get('list_id')}", extra={
        'user_ip': get_client_ip(request), 'user_email': request.user.email})
    
    context = return_default_templates_context(request)
    return render(request, 'company/includes/templates/templates_lists.html', context=context)


def get_templates_table(request: HttpRequest, list_id: int):
    user, page = request.user, request.GET.get('page', 1)
    paginator = get_paginated_queryset(Template.objects.filter(template_list_id=list_id, template_list__user=user), page)
        
    transfer_template_form = TransferTemplate(templates_lists=TemplatesList.objects.filter(user=user).select_related('user'))

    context = {
        'list_id': list_id,
        'paginator': paginator,
        'transfer_template_form': transfer_template_form
    }
    return render(request, 'company/includes/templates/templates_table.html', context=context)


def create_template(request: HttpRequest, list_id: int):
    data = json.loads(request.body.decode('utf-8'))
    template_name, subject_line, message = data.get('name_template'), data.get('subject_line'), data.get('message')

    Template.objects.create(template_list_id=list_id, template_name=template_name, subject_line=subject_line, message=message)

    context = return_default_templates_context(request, list_id)
    return render(request, 'company/includes/templates/templates_lists.html', context=context)


def edit_tempalte(request: HttpRequest, list_id: int):
    user, data = request.user, json.loads(request.body.decode('utf-8'))
    Template.objects.filter(pk=data.get('template_id'), template_list_id=list_id, template_list__user=user).update(template_name=data.get('name_template'), subject_line=data.get('subject_line'), message=data.get('message'))
    context = return_default_templates_context(request, list_id)
    return render(request, 'company/includes/templates/templates_lists.html', context=context)


def transfer_template(request: HttpRequest, list_id: int):
    user, data = request.user, json.loads(request.body.decode('utf-8'))
    Template.objects.filter(pk=data.get('template_id'), template_list_id=list_id, template_list__user=user).update(template_list_id=data.get('new_list_id'))
    context = return_default_templates_context(request, list_id)
    return render(request, 'company/includes/templates/templates_lists.html', context=context)


def delete_tempalte(request: HttpRequest, list_id: int):
    user, data = request.user, json.loads(request.body.decode('utf-8'))
    Template.objects.filter(pk=data.get('template_id'), template_list_id=list_id, template_list__user=user).delete()
    context = return_default_templates_context(request, list_id)
    return render(request, 'company/includes/templates/templates_lists.html', context=context)


def templates_actions(request: HttpRequest):
    user, data = request.user, json.loads(request.body.decode('utf-8'))
    list_id, templates_ids, action, trans_id = data.get('list_id'), list(map(int, data.get('templates'))), data.get('action'), data.get('trans_id')
    templates = Template.objects.filter(pk__in=templates_ids, template_list__user=user, template_list_id=list_id)

    if action == 'del': templates.delete()
    elif action == 'trans':templates.update(template_list_id=trans_id)

    context = return_default_templates_context(request, list_id)
    return render(request, 'company/includes/templates/templates_lists.html', context=context)


def get_newsletters(request: HttpRequest, list_id: int | None = None):
    context = return_default_newsletters_context(request, list_id)
    return render(request, 'company/newsletter_templates.html', context=context)


def create_newsletters_list(request: HttpRequest):
    user, data = request.user, json.loads(request.body.decode('utf-8'))
    new_list = NewsletterTemplatesList.objects.create(user=user, list_name=data.get('list_name'))
    context = return_default_newsletters_context(request, new_list.pk)
    return render(request, 'company/includes/newsletters/newsletters_lists.html', context=context)


def edit_newsletters_list(request: HttpRequest, list_id: int):
    user, data = request.user, json.loads(request.body.decode('utf-8'))
    NewsletterTemplatesList.objects.filter(pk=list_id, user=user).update(list_name=data.get('name_list'))
    context = return_default_newsletters_context(request, list_id)
    return render(request, 'company/includes/newsletters/newsletters_lists.html', context=context)


def delete_newsletters_list(request: HttpRequest):
    user, data = request.user, json.loads(request.body.decode('utf-8'))
    NewsletterTemplatesList.objects.filter(pk=data.get('list_id'), user=user).delete()
    context = return_default_newsletters_context(request)
    return render(request, 'company/includes/newsletters/newsletters_lists.html', context=context)


def get_add_newsletter_template_page(request: HttpRequest, list_id: int):
    set_template_form = SetTemplateForm(user=request.user)
    context = {
        'list_id': list_id,
        'set_template_form': set_template_form,
    }
    return render(request, 'company/add_newsletter_page.html', context=context)


def get_edit_newsletter_template_page(request: HttpRequest, list_id: int, newsletter_id: int):
    user, newsletter = request.user, NewsletterTemplate.objects.get(pk=newsletter_id)

    if newsletter.newsletter_list.user != user:
        messages.error(request, gettext_lazy("You don't have access"))
        return redirect('newsletters', list_id=list_id)

    set_template_form = SetTemplateForm(user=request.user)
    context = {
        'visual': newsletter.visual,
        'name': newsletter.newsletter_name,
        'list_id': list_id,
        'newsletter_id': newsletter_id,
        'set_template_form': set_template_form,
        'data': newsletter.data,
        'pop_up_data': newsletter.pop_up_data,
    }
    return render(request, 'company/edit_newsletter_page.html', context=context)


def get_newsletters_table(request: HttpRequest, list_id: int):
    user, page = request.user, request.GET.get('page', 1)
    paginator = get_paginated_queryset(NewsletterTemplate.objects.filter(newsletter_list_id=list_id, newsletter_list__user=user), page)
        
    transfer_newsletter_form = TransferNewsletter(newsletters_lists=NewsletterTemplatesList.objects.filter(user=user).select_related('user'))

    context = {
        'list_id': list_id,
        'paginator': paginator,
        'transfer_newsletter_form': transfer_newsletter_form
    }
    return render(request, 'company/includes/newsletters/newsletters_table.html', context=context)


def add_newsletter_template(request: HttpRequest, list_id: int):
    user: UserModel = request.user

    source = request.POST.get('draganddropjson')
    data = json.loads(source)['data']
    popups_data = json.loads(source)['popups_data']
    visual = json.loads(source)['diagram']

    sequence = parse_email_to_sequence(user, data) if data else None

    newsletter_fields = {
        'newsletter_list_id': list_id,
        'sequence': json.dumps(sequence),
        'visual': json.dumps(visual),
        'data': json.dumps(data),
        'pop_up_data': json.dumps(popups_data),
        'newsletter_name': request.POST.get('newsletter_name')
    }
    NewsletterTemplate.objects.create(**newsletter_fields)
    return redirect('newsletters', list_id=list_id)


def edit_newsletter_template(request: HttpRequest, list_id: int, newsletter_id: int):
    user, newsletter = request.user, NewsletterTemplate.objects.get(pk=newsletter_id)

    if newsletter.newsletter_list.user != user:
        messages.error(request, gettext_lazy("You don't have access"))
        return redirect('newsletters', list_id=list_id)

    source = request.POST.get('draganddropjson')
    data = json.loads(source)['data']
    popups_data = json.loads(source)['popups_data']
    visual = json.loads(source)['diagram']

    sequence = parse_email_to_sequence(user, data) if data else None

    newsletter.newsletter_name = request.POST.get('newsletter_name')
    newsletter.visual = json.dumps(visual)
    newsletter.data = json.dumps(data)
    newsletter.pop_up_data = json.dumps(popups_data)
    newsletter.sequence = json.dumps(sequence)
    newsletter.save()
    return redirect('newsletters', list_id=list_id)


def transfer_newsletter(request: HttpRequest, list_id: int):
    user, data = request.user, json.loads(request.body.decode('utf-8'))
    NewsletterTemplate.objects.filter(pk=data.get('newsletter_id'), newsletter_list_id=list_id, newsletter_list__user=user).update(newsletter_list_id=data.get('new_list_id'))
    context = return_default_newsletters_context(request, list_id)
    return render(request, 'company/includes/newsletters/newsletters_lists.html', context=context)


def delete_newsletter(request: HttpRequest, list_id: int):
    user, data = request.user, json.loads(request.body.decode('utf-8'))
    NewsletterTemplate.objects.filter(pk=data.get('newsletter_id'), newsletter_list_id=list_id, newsletter_list__user=user).delete()
    context = return_default_newsletters_context(request, list_id)
    return render(request, 'company/includes/newsletters/newsletters_lists.html', context=context)


def newsletters_actions(request: HttpRequest):
    user, data = request.user, json.loads(request.body.decode('utf-8'))
    list_id, newsletters_ids, action, trans_id = data.get('list_id'), list(map(int, data.get('newsletters'))), data.get('action'), data.get('trans_id')
    newsletters = NewsletterTemplate.objects.filter(pk__in=newsletters_ids, newsletter_list__user=user, newsletter_list_id=list_id)

    if action == 'del': newsletters.delete()
    elif action == 'trans':newsletters.update(newsletter_list_id=trans_id)

    context = return_default_newsletters_context(request, list_id)
    return render(request, 'company/includes/newsletters/newsletters_lists.html', context=context)


def get_sending_mails(request: HttpRequest, list_id: int | None = None):
    context = return_default_sendings_context(request, list_id)
    return render(request, 'company/sending_mails_page.html', context=context)


def create_sending(request: HttpRequest):
    data = json.loads(request.body.decode('utf-8'))
    list_name = data.get('list_name')
    add_list_form_templates = data.get('add_list_form_templates')
    add_list_form_users_lists = data.get('add_list_form_users_lists')

    context = return_default_sendings_context(request)

    if not (add_list_form_users_lists and add_list_form_templates):
        messages.error(request, gettext_lazy('You have not selected a list of clients or newsletter templates!'))
        return render(request, 'company/includes/sendings/sending_mails_lists.html', context=context)

    users_list = List.objects.get(pk=add_list_form_users_lists)

    if not (containers := ListContainer.objects.filter(list=users_list)).exists():
        messages.error(request, f"{gettext_lazy('There are no clients in your')}  {users_list.list_name} {gettext_lazy('list. To create mailing add clients')}")
        return render(request, 'company/includes/sendings/sending_mails_lists.html', context=context)

    users = [list_container.contact for list_container in containers]

    if not users:
        messages.error(request, f"{gettext_lazy('There are no clients in your')}  {users_list.list_name} {gettext_lazy('list. To create mailing add clients')}")
        return render(request, 'company/includes/sendings/sending_mails_lists.html', context=context)
    
    with transaction.atomic():
        sending_mails_list = SendingMailsList.objects.create(list_name=list_name, newsletter_id=add_list_form_templates, owner=request.user)
        sequence = json.loads(sending_mails_list.newsletter.sequence)

        for _user in users: create_mails_for_user(request, _user, sending_mails_list, sequence)
        
        context = return_default_sendings_context(request, sending_mails_list.pk)
        return render(request, 'company/includes/sendings/sending_mails_lists.html', context=context)


def edit_sendings_list(request: HttpRequest, list_id: int):
    user, data = request.user, json.loads(request.body.decode('utf-8'))
    SendingMailsList.objects.filter(pk=list_id, owner=user).update(list_name=data.get('name_list'))
    context = return_default_sendings_context(request, list_id)
    return render(request, 'company/includes/sendings/sending_mails_lists.html', context=context)


def delete_sendings_list(request: HttpRequest):
    user, data = request.user, json.loads(request.body.decode('utf-8'))
    SendingMailsList.objects.filter(pk=data.get('list_id'), owner=user).delete()
    context = return_default_sendings_context(request)
    return render(request, 'company/includes/sendings/sending_mails_lists.html', context=context)


def break_sending(request: HttpRequest, list_id: int):
    user, data = request.user, json.loads(request.body.decode('utf-8'))
    SendingMails.objects.filter(pk=data.get('sending_id'), sendingmails_list_id=list_id, sendingmails_list__owner=user).update(active=False, status='Cancelled') if SendingMails.objects.filter(pk=data.get('sending_id'), sendingmails_list_id=list_id, sendingmails_list__owner=user).exists() else SendingTelegram.objects.filter(pk=data.get('sending_id'), sendingmails_list_id=list_id, sendingmails_list__owner=user).update(active=False, status='Cancelled')
    context = return_default_sendings_context(request, list_id)
    return render(request, 'company/includes/sendings/sending_mails_lists.html', context=context)


def delete_sending(request: HttpRequest, list_id: int):
    user, data = request.user, json.loads(request.body.decode('utf-8'))
    SendingMails.objects.filter(pk=data.get('sending_id'), sendingmails_list_id=list_id, sendingmails_list__owner=user).delete() if SendingMails.objects.filter(pk=data.get('sending_id'), sendingmails_list_id=list_id, sendingmails_list__owner=user).exists() else SendingTelegram.objects.get(pk=data.get('sending_id'), sendingmails_list_id=list_id, sendingmails_list__owner=user).delete()
    context = return_default_sendings_context(request, list_id)
    return render(request, 'company/includes/sendings/sending_mails_lists.html', context=context)


def start_sendingmails(request: HttpRequest, list_id: int):

    user, data = request.user, json.loads(request.body.decode('utf-8'))

    context = return_default_sendings_context(request, list_id)

    if (sending_time := data.get('sending_time_radio') == 'later') and not (start_time := data.get('sending_time_input')):
        response_context = {
            'message': gettext_lazy('Please enter a positive number'),
            'message_type': 'error',
            'html': render_to_string(request=request, template_name='company/includes/sendings/sending_mails_lists.html', context=context)
        }
        return JsonResponse(response_context)

    emails = SendingMails.objects.filter(sendingmails_list_id=list_id, sendingmails_list__owner=user, status='Pending', active=False)
    telegram_messages = SendingTelegram.objects.filter(sendingmails_list_id=list_id, sendingmails_list__owner=user, status='Pending',
                                                       active=False) if TelegramBot.objects.filter(user=request.user,
                                                                                                   is_using=True).exists() else SendingTelegram.objects.none()
    if not (emails.count() or telegram_messages.count()):
        response_context = {
            'message': gettext_lazy('There are no mails in your mailing!'),
            'message_type': 'error',
            'html': render_to_string(request=request, template_name='company/includes/sendings/sending_mails_lists.html', context=context)
        }
        return JsonResponse(response_context)
    
    utc_start_time = timezone.now()
    if sending_time:
        start_time = datetime.strptime(start_time, '%Y-%m-%dT%H:%M')
        user_timezone = pytz.timezone(user.local_timezone)
        start_time = user_timezone.localize(start_time)
        utc_start_time = start_time.astimezone(pytz.utc)

    min_time = min([email.date for email in emails] + [email.date for email in telegram_messages])
    delta = utc_start_time - min_time - timedelta(seconds=1)


    not_already_started = [not (email.status == 'Delivered' or "Error" in email.status or "Opened" in email.status) for
                           email in emails]
    not_already_started_tg = [not (email.status == 'Delivered' or "Error" in email.status or "Opened" in email.status)
                              for email in telegram_messages]

    if any(not_already_started): emails.update(date=F('date') + delta, status='Pending', active=True)
    if any(not_already_started_tg): telegram_messages.update(date=F('date') + delta, status='Pending', active=True)

    context = return_default_sendings_context(request, list_id)
    response_context = {
        'message': gettext_lazy('Sendings successfully started'),
        'message_type': 'success',
        'html': render_to_string(request=request, template_name='company/includes/sendings/sending_mails_lists.html', context=context)
    }
    return JsonResponse(response_context)


def stop_sendingmails(request: HttpRequest, list_id: int):
    user = request.user
    SendingMails.objects.filter(sendingmails_list_id=list_id, sendingmails_list__owner=user, status='Pending').update(active=False, status='Cancelled')
    SendingTelegram.objects.filter(sendingmails_list_id=list_id, sendingmails_list__owner=user, status='Pending').update(active=False, status='Cancelled')
    context = return_default_sendings_context(request, list_id)
    return render(request, 'company/includes/sendings/sending_mails_lists.html', context=context)


def refresh_sending_page(request: HttpRequest, list_id: int):
    context = return_default_sendings_context(request, list_id)
    return render(request, 'company/includes/sendings/sending_mails_lists.html', context=context)


def get_sending_table(request: HttpRequest, list_id: int):
    page, statuses, lang = request.GET.get('page', 1), request.GET.getlist(
        'statuses[]'), request.LANGUAGE_CODE

    emails = SendingMails.objects.filter(sendingmails_list_id=list_id).select_related('sendingmails_list', 'recipient')
    telegram_mails = SendingTelegram.objects.filter(sendingmails_list_id=list_id).select_related('sendingmails_list', 'recipient')

    activate_language('en')
    statuses = [SendingAbstrat.statuses[int(status_id)][1] for status_id in statuses]

    if statuses:
        emails, telegram_mails = emails.filter(status__in=statuses), telegram_mails.filter(status__in=statuses)
    activate_language(lang)

    paginator = get_paginated_queryset(list(emails) + list(telegram_mails), page)
    context = {
        'list_id': list_id,
        'paginator': paginator,
    }
    return render(request, 'company/includes/sendings/sending_mails_table.html', context=context)


def sending_actions(request: HttpRequest):
    data = json.loads(request.body.decode('utf-8'))
    list_id, emails, telegrams, action = data.get('list_id'), list(map(int, data.get('emails'))), list(map(int, data.get('telegrams'))), data.get('action')
    emails = SendingMails.objects.filter(pk__in=emails, sendingmails_list__owner=request.user, sendingmails_list_id=list_id)
    telegrams = SendingTelegram.objects.filter(pk__in=telegrams, sendingmails_list__owner=request.user, sendingmails_list_id=list_id)

    if action == 'del':
        emails.delete()
        telegrams.delete()
    elif action == 'break':
        emails_pending = emails.filter(status='Pending', active=True)
        telegrams_pending = telegrams.filter(status='Pending', active=True)

        if (set(emails) - set(emails_pending)) or (set(telegrams) - set(telegrams_pending)):
            messages.warning(request, gettext_lazy('Inactive sendings have not been canceled'))

        emails_pending.update(status='Cancelled')
        telegrams_pending.update(status='Cancelled')

    context = return_default_sendings_context(request, list_id)
    return render(request, 'company/includes/sendings/sending_mails_lists.html', context=context)


def find_clients_page(request: HttpRequest):
    find_by_feature_form = FindContactByFeature()

    context = {
        'find_by_feature_form': find_by_feature_form,
        'byname': 'byname',
        'bydomain': 'bydomain',
        'byfeature': 'byfeature'
    }

    return render(request, 'company/find_clients_base.html', context=context)


def find_clients_by_name(request: HttpRequest):
    user, data = request.user, json.loads(request.body.decode('utf-8'))

    context = {
        'by': 'byname',
        'name': data.get('name'),
        'surname': data.get('surname'),
        'domain': data.get('domain')
    }

    if not ((name := data.get('name')) and (surname := data.get('surname')) and (domain := data.get('domain'))):
        messages.warning(request, gettext_lazy('Fill in all the fields'))
        return render(request, 'company/includes/find_clients/by_name_table.html', context=context)

    name_ru = translit(name, language_code='ru')
    surname_ru = translit(surname, language_code='ru')

    name_lat = translit(name, language_code='ru', reversed=True)
    surname_lat = translit(surname, language_code='ru', reversed=True)

    filters = {
        'name__icontains': name_lat,
        'surname__icontains': surname_lat,
        'company__company_site__icontains': domain
    }

    # contacts = Contact.objects.filter(**filters).select_related('company', 'company__company_branch', 'company__company_size')

    with transaction.atomic():
        search_credit_count_down(user.id)

        find_emails_fields = {
            'request_for_search__name': name_ru,
            'request_for_search__surname': surname_ru,
            'request_for_search__name_lat': name_lat,
            'request_for_search__surname_lat': surname_lat,
            'request_for_search__company_domain': domain
        }
        if (find_emails := FindEmails.objects.filter(**find_emails_fields)).exists():

            mails_data: dict[str, bool] = {find_email.email: find_email.get_status_display() for find_email in find_emails}
            context.update({'mails_data': mails_data})
            return render(request, 'company/includes/find_clients/by_name_table.html', context=context)


        request_for_search = RequestsForSearch.objects.create(name=name_ru, surname=surname_ru, name_lat=name_lat, surname_lat=surname_lat, company_domain=domain)
        found_contacts: QuerySet[Contact] = Contact.objects.filter(email__iendswith=domain)

        if found_contacts.exists():
            pattern_nums = [pattern_num for similar_contact in found_contacts if (pattern_num := get_pattern_number_by_email(similar_contact.email, similar_contact.name, similar_contact.surname, domain))]
            mails: dict | None = get_email_by_pattern_nums(name_lat, surname_lat, domain, pattern_nums) if pattern_nums else None

        if not found_contacts.exists() or not mails:
            mails: dict = get_emails_new(name_lat, surname_lat, domain)

        mails_data = {}
        if mails:
            found_emails: list[FindEmails] = [
                FindEmails(email=email, request_for_search=request_for_search, status=FindEmails.VALID if status else FindEmails.PROBABLY) for email, status in mails.items() if status
            ]
            if found_emails: mails_data: dict[str, bool] = {email.email: email.get_status_display() for email in FindEmails.objects.bulk_create(found_emails)}

            contacts_for_save = [Contact(name=name_ru, surname=surname_ru, email=email) for email, status in mails.items() if status and not Contact.objects.filter(name=name_ru, surname=surname_ru, email=email).exists()]
            Contact.objects.bulk_create(contacts_for_save)
        else:
            messages.add_message(request, messages.ERROR, gettext_lazy("It's a pity that nothing was found, repeat the search in a couple of days, by that time our algorithms will find something new for this company"))
        
        context.update({'mails_data': mails_data})
        return render(request, 'company/includes/find_clients/by_name_table.html', context=context)
        

def find_clients_by_domain(request: HttpRequest):
    user, data, page = request.user, json.loads(request.body.decode('utf-8')), request.GET.get('page', 1)
    domain = data.get('domain')
    
    context = {
        'by': 'bydomain',
        'domain': domain
    }

    filters = {'company__company_site__iexact': domain}
    contacts = Contact.objects.filter(**filters).select_related('company', 'company__company_branch', 'company__company_size')

    paginator = get_paginated_queryset(contacts, page)

    if paginator['queryset']:
        context.update({'paginator': paginator})
        return render(request, 'company/includes/find_clients/by_domain_table.html', context=context)
    
    RequestsForSearch.objects.create(name=None, surname=None, name_lat=None, surname_lat=None, company_domain=domain)
    messages.add_message(request, messages.ERROR, gettext_lazy("It's a pity that nothing was found, repeat the search in a couple of days, by that time our algorithms will find something new for this company"))

    return render(request, 'company/includes/find_clients/by_domain_table.html', context=context)


def find_clients_by_feature(request: HttpRequest):
    user, data = request.user, json.loads(request.body.decode('utf-8'))

    company_size = data.get('company_size')
    company_branch = data.get('company_branch')

    context = {
        'by': 'byfeature',
        'company_size': company_size,
        'company_branch': company_branch
    }

    filters = {}
    if company_size and company_size != 'None':
        filters['company__company_size__size'] = company_size
    if company_branch and company_branch != 'None':
        filters['company__company_branch__industry_ru'] = company_branch
    
    contacts = Contact.objects.filter(**filters).select_related('company', 'company__company_branch', 'company__company_size')

    paginator = get_paginated_queryset(contacts)

    if not paginator['queryset']:
        messages.add_message(request, messages.ERROR, gettext_lazy("It's a pity that nothing was found, repeat the search in a couple of days, by that time our algorithms will find something new for this company"))
        return render(request, 'company/includes/find_clients/by_feature_table.html', context=context)

    context.update({'paginator': paginator})
    return render(request, 'company/includes/find_clients/by_feature_table.html', context=context)