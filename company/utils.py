import json
import pytracking

import chardet
import charset_normalizer
import unicodedata

from concurrent.futures import as_completed

import requests
from requests_futures.sessions import FuturesSession

from datetime import timedelta
from django.utils import timezone

from SalesTech.settings import MILLIONVERIFIER_API_KEY, VERIFIER_URL
from company.models import *
from company.scheduler import get_smtp_settings
from .pagination import get_paginated_queryset

from logger.models import Logs


def search_credit_count_limited(user_id):
    user = UserModel.objects.get(pk=user_id)
    current_company = user.company
    return current_company.search_credit_count <= 0


def search_credit_count_down(user_id):
    user: UserModel = UserModel.objects.get(pk=user_id)
    current_company = user.company
    current_company.search_credit_count -= 1
    current_company.save()
    user.used_search_credit_count += 1
    user.save()


def detect_encoding(filename):
    with open(filename, 'rb') as f:
        # 1. Определение кодировки с помощью модуля chardet
        result = chardet.detect(f.read())

        # 2. Определение кодировки с помощью модуля charset_normalizer
        if result['encoding'] is None:
            f.seek(0)
            result = charset_normalizer.detect(f.read())

        # 3. Ручное определение кодировки
        if result['encoding'] is None:
            f.seek(0)
            content = f.read()
            for encoding in ['utf-8', 'windows-1251', 'iso-8859-1']:
                try:
                    decoded_content = content.decode(encoding)
                    result['encoding'] = encoding
                    break
                except UnicodeDecodeError:
                    pass

    # 4. Проверка содержимого файла на наличие неизвестных символов
    with open(filename, encoding=result['encoding']) as f:
        content = f.read()

    for char in content:
        try:
            unicodedata.name(char)
        except ValueError:
            pass

    return result['encoding']


def get_emails(name: str, surname: str, domain: str, user_id: int):
    data = {}
    verifier_url = f'https://api.millionverifier.com/api/v3/?api={MILLIONVERIFIER_API_KEY}&email='
    with FuturesSession() as session:
        emails_list = [
            session.get(f'{verifier_url}"{name.lower()}.{surname.lower()}@{domain}"&timeout=1'),
            session.get(f'{verifier_url}"{surname.lower()}.{name.lower()}@{domain}"&timeout=1'),
            session.get(f'{verifier_url}"{name.lower()[0]}.{surname.lower()}@{domain}"&timeout=1'),
            session.get(f'{verifier_url}"{surname.lower()}.{name.lower()[0]}@{domain}"&timeout=1'),
            session.get(f'{verifier_url}"{surname.lower()[0]}{name.lower()[0]}@{domain}"&timeout=1'),
            session.get(f'{verifier_url}"{name.lower()[0]}{surname.lower()}@{domain}"&timeout=1'),
            session.get(f'{verifier_url}"{name.lower()}@{domain}"&timeout=1'),
            session.get(f'{verifier_url}"{surname.lower()}@{domain}"&timeout=1'),
            session.get(f'{verifier_url}"{name.lower()[0]}_{surname.lower()}@{domain}"&timeout=1'),
            session.get(f'{verifier_url}"{name.lower()[:2]}{surname.lower()[:3]}@{domain}"&timeout=1'),
            session.get(f'{verifier_url}"{name.lower()}{surname.lower()}@{domain}"&timeout=1'),
            session.get(f'{verifier_url}"{name.lower()}_{surname.lower()}@{domain}"&timeout=1'),
            session.get(f'{verifier_url}"{surname.lower()}_{name.lower()}@{domain}"&timeout=1'),
            session.get(f'{verifier_url}"{surname.lower()}_{name.lower()}@{domain}"&timeout=1'),
            session.get(f'{verifier_url}"{surname.lower()}{name.lower()[0]}@{domain}"&timeout=1'),
            session.get(f'{verifier_url}"{surname.lower()[0]}{name.lower()}@{domain}"&timeout=1'),
            session.get(f'{verifier_url}"{name.lower()}{surname.lower()[0]}@{domain}"&timeout=1'),
            session.get(f'{verifier_url}"{name.lower()[:3]}{surname.lower()[:3]}@{domain}"&timeout=1'),
            session.get(f'{verifier_url}"{surname.lower()[:3]}{name.lower()[:3]}@{domain}"&timeout=1'),
            session.get(f'{verifier_url}"iam.{name.lower()}{surname.lower()}@{domain}"&timeout=1'),
            session.get(f'{verifier_url}"iam.{surname.lower()}{name.lower()}@{domain}"&timeout=1'),
        ]

        for future in as_completed(emails_list):
            result = future.result().json()
            data.update({result['email']: result['result'] == 'ok' or result['subresult'] == 'ok'})

    Logs.info(f"Отправлено: {len(emails_list)} запросов. Успешных: {len(data)} запросов. ID пользователя: {user_id}",
              Logs.MILLIONVERIFIER)

    return data


def generate_emails(name: str, surname: str, domain: str):
    return [f"{name.lower()}.{surname.lower()}@{domain}",
            f"{surname.lower()}.{name.lower()}@{domain}",
            f"{name.lower()[0]}.{surname.lower()}@{domain}",
            f"{surname.lower()}.{name.lower()[0]}@{domain}",
            f"{surname.lower()[0]}{name.lower()[0]}@{domain}",
            f"{name.lower()[0]}{surname.lower()}@{domain}",
            f"{name.lower()}@{domain}",
            f"{surname.lower()}@{domain}",
            f"{name.lower()[0]}_{surname.lower()}@{domain}",
            f"{name.lower()[:2]}{surname.lower()[:3]}@{domain}",
            f"{name.lower()}{surname.lower()}@{domain}",
            f"{name.lower()}_{surname.lower()}@{domain}",
            f"{surname.lower()}_{name.lower()}@{domain}",
            f"{surname.lower()}_{name.lower()}@{domain}",
            f"{surname.lower()}{name.lower()[0]}@{domain}",
            f"{surname.lower()[0]}{name.lower()}@{domain}",
            f"{name.lower()}{surname.lower()[0]}@{domain}",
            f"{name.lower()[:3]}{surname.lower()[:3]}@{domain}",
            f"{surname.lower()[:3]}{name.lower()[:3]}@{domain}",
            f"iam.{name.lower()}{surname.lower()}@{domain}",
            f"iam.{surname.lower()}{name.lower()}@{domain}"]


def get_pattern_number_by_email(email, fname, lname, domain):
    generated = generate_emails(fname, lname, domain)
    if email in generated:
        return generated.index(email)
    return None


def get_emails_new(name: str, surname: str, domain: str):
    email_list_json = json.dumps(generate_emails(name, surname, domain))
    r = requests.post(f"{VERIFIER_URL}/validate_emails/", data=email_list_json)
    return r.json()['results']


def get_email_by_pattern_nums(name, surname, domain, pattern_nums):
    email_json = json.dumps([generate_emails(name, surname, domain)[i] for i in pattern_nums if i])

    r = requests.post(f"{VERIFIER_URL}/validate_emails/", data=email_json)
    return r.json()['results']


def email_sequence(user: UserModel, data: dict, item: dict, index: str):
    if 'template_name' in item.keys():
        if TemplatesList.objects.filter(user=user).exists():
            template_list = TemplatesList.objects.filter(
                user=user).first()
        else:
            template_list = TemplatesList.objects.create(
                user=user, list_name='DEFAULT')

        current_template: Template = Template.objects.create(
            template_list=template_list,
            template_name=item['template_name'],
            subject_line=item['edit_subject_line'],
            message=item['msg_text'])

    else:
        current_template = Template.objects.get(
            pk=int(item['template_id']))

    data[index] = {
        'type': 'EMAIL_TEMPLATE',
        'name': f'{current_template.template_name}',
        'message': item['msg_text'],
        "subject_line": item['edit_subject_line'],
    }

    return data


def telegram_sequence(user: UserModel, data: dict, item: dict, index: str):
    if 'tg_template_name' in item.keys():
        if TemplatesList.objects.filter(user=user).exists():
            template_list = TemplatesList.objects.filter(user=user).first()
        else:
            template_list = TemplatesList.objects.create(user=user, list_name='DEFAULT')

        current_template: Template = Template.objects.create(
            template_list=template_list,
            template_name=item['tg_template_name'],
            subject_line=item['tg_subject_line'],
            message=item['tg_msg'])

    else:
        current_template = Template.objects.get(pk=int(item['tg_template_id']))

    data[index] = {
        'type': 'TELEGRAM',
        'name': f'{current_template.template_name}',
        'message': item['tg_msg'],
        "subject_line": item['tg_subject_line'],
    }

    return data


def delay_sequence(item: dict, data: dict, index: str):
    delay = int(item['delay']) * 60

    data[index] = {
        'type': 'DELAY',
        'value': delay
    }

    return data


def goal_sequence(item: dict, data: dict, index: str):
    data[index] = {
        'type': 'GOAL',
        'value': item['goal']
    }

    return data


def trigger_sequence(user: UserModel, data: dict, item: dict, index: str):
    if item['trigger_time'] == 'days':
        trigger_minutes = int(item['trigger']) * 1440
    elif item['trigger_time'] == 'hours':
        trigger_minutes = int(item['trigger']) * 60
    elif item['trigger_time'] == 'minutes':
        trigger_minutes = int(item['trigger'])

    trigger_yes, trigger_no = parse_email_to_sequence(
        user, item['yes']), parse_email_to_sequence(user, item['no'])

    data[index] = {
        'type': 'TRIGGER',
        'condition': {
            'type': 'EMAIL_OPENED',
            'timeout': trigger_minutes
        },
        'value': {
            'YES': trigger_yes,
            'NO': trigger_no
        }
    }

    return data


def parse_email_to_sequence(user, popup_data):
    data = {}
    for _data in popup_data:
        index = str(len(data))

        key = list(_data.keys())[0]
        item: dict = _data[key]

        if 'edit_subject_line' in item.keys():
            data = email_sequence(user, data, item, index)

        elif 'tg_subject_line' in item.keys():
            data = telegram_sequence(user, data, item, index)

        elif 'delay' in item.keys():
            data = delay_sequence(item, data, index)

        elif 'goal' in item.keys():
            data = goal_sequence(item, data, index)

        elif 'trigger' in item.keys():
            data = trigger_sequence(user, data, item, index)

    return data


def replace_contact_values(message, contact):
    new_message = message
    current_contact = contact
    fields = [f.name for f in current_contact._meta.get_fields()]
    for field in fields:
        find = f"{{{{{field}}}}}"
        try:
            if find == '{{middle_name}}':
                new_message = new_message.replace(
                    "{{middlename}}", getattr(current_contact, field))
            elif find == '{{phone}}':
                phone_number = getattr(current_contact, field)
                new_message = new_message.replace(
                    "{{phone_number}}", phone_number.as_e164)
            elif find == "{{company}}":
                company = getattr(current_contact, field)
                new_message = new_message.replace(
                    "{{company_name}}", company.company_name)
                new_message = new_message.replace(
                    "{{company_site}}", company.company_site)
            elif find == "{{position_in_company}}":
                new_message = new_message.replace(
                    "{{position}}", getattr(current_contact, field))
            else:
                value = getattr(current_contact, field)
                new_message = new_message.replace(find, value)
        except Exception as e:
            pass

    return new_message


def create_pixel_link(email_id, request):
    domain = request.build_absolute_uri('/')
    language = lang if (lang := request.LANGUAGE_CODE) else 'en'

    open_tracking_url = pytracking.get_open_tracking_url(
        {"email_id": email_id}, base_open_tracking_url=f"{domain}{language}/company/open/",
    )

    return open_tracking_url


def create_mails_for_user(request, user, mail_list, sequence, positive_way=True, message=None, trigger_type=None,
                          trigger_delay=None):
    if not (message or trigger_type or trigger_delay):
        conditions = None
        delay = timezone.now()

    else:
        if not positive_way:
            text = "NOT_" + trigger_type
        else:
            text = trigger_type
        previous_message = SendingMails.objects.get(pk=message)
        if previous_message.conditions == 'null':
            conditions = []
        else:
            conditions = json.loads(previous_message.conditions)
        conditions.append((text, message))
        delay = previous_message.date + timedelta(minutes=trigger_delay)

    for elem in sequence.items():
        if elem[1]['type'] == 'EMAIL_TEMPLATE':
            message, theme, template_name = elem[1]['message'], elem[1]['subject_line'], elem[1]['name']

            current_mail = SendingMails(
                sendingmails_list=mail_list,
                message=replace_contact_values(
                    message, user),
                theme=replace_contact_values(
                    theme, user),
                recipient=user, link='link', status='Pending',
                date=delay,
                active=False, template_name=template_name, conditions=json.dumps(conditions)
            )
            current_mail.save()
            current_mail.link = create_pixel_link(current_mail.id, request)
            settings, owner = get_smtp_settings(current_mail)

            current_mail.save()
            previous_message = current_mail.id

        elif elem[1]['type'] == 'TELEGRAM':
            message, theme, template_name = elem[1]['message'], elem[1]['subject_line'], elem[1]['name']

            current_mail = SendingTelegram.objects.create(
                sendingmails_list=mail_list,
                message=replace_contact_values(
                    message, user),
                theme=replace_contact_values(
                    theme, user),
                recipient=user, status='Pending',
                date=delay,
                active=False, template_name=template_name
            )
            previous_message = current_mail.id

        elif elem[1]['type'] == 'DELAY':
            delay += timedelta(minutes=elem[1]['value'])
        elif elem[1]['type'] == 'TRIGGER':
            delta = elem[1]['condition']['timeout']
            type = elem[1]['condition']['type']
            ways = elem[1]['value']
            create_mails_for_user(request, user, mail_list, ways['YES'], positive_way=True,
                                  message=previous_message,
                                  trigger_type=type, trigger_delay=delta)
            create_mails_for_user(request, user, mail_list, ways['NO'], positive_way=False,
                                  message=previous_message,
                                  trigger_type=type, trigger_delay=delta)


def csv_to_dict(csv_file_path):
    import csv
    with open(csv_file_path, 'r', encoding=detect_encoding(csv_file_path), errors='ignore') as csv_file:
        try:
            dialect = csv.Sniffer().sniff(csv_file.read(1024))
        except:
            return 'dialect_error'
        csv_file.seek(0)
        reader = csv.DictReader(csv_file, dialect=dialect)
        data = [row for row in reader]
    return data


def build_contacts_from_csv(csv_file_path, is_user_contacts: bool):
    raw_data: str | list[dict] = csv_to_dict(csv_file_path)

    if raw_data == 'dialect_error':
        return raw_data

    # Список контактов, которые мы создали(т.е их еще не было в базе)
    created_contacts = set()

    for contact in raw_data:

        if not contact.get('Email'):
            continue

        # Вытаскиваем данные контакта в нужном нам формате
        essential_contact_data = {'name': contact.get('First name'),
                                  'surname': contact.get('Last name'),
                                  'email': contact.get('Email'),
                                  'position_in_company': contact.get('Job position')}
        # Смотрим, есть ли данные о компании контакта в csv
        # Если инфа о компании существует, то пытаемся найти эту компанию в БД по урле на сайт компании и ее названию
        # Находим в БД или создаем компанию по ее урлу

        company_defaults = {'company_name': contact.get('Company name'),
                            'company_site': contact.get('Company url')}

        if contact.get('Company industry'):
            company_defaults['company_branch'], branch_created = CompanyBranch.objects.get_or_create(
                industry=contact.get('Company industry'))

        if contact.get('Company size'):
            company_defaults['company_size'], size_created = CompanySizes.objects.get_or_create(
                size=contact.get('Company size'))

        company_for_contact, created = ContactCompany.objects.get_or_create(
            company_site__iexact=contact['Company url'],
            company_name__iexact=contact['Company name'], defaults=company_defaults
        )

        if is_user_contacts:
            contact_db_record = UsersContacts(**essential_contact_data, company=company_for_contact)
        else:
            contact_db_record = Contact(**essential_contact_data, company=company_for_contact)

        created_contacts.add(contact_db_record)

    if is_user_contacts:
        return UsersContacts.objects.bulk_create(created_contacts)

    return Contact.objects.bulk_create(created_contacts)


def handle_uploaded_csv(file, user: UserModel, is_user_contacts: bool, list_id=None):
    import os

    temp_file_name = f"{user.id}_{file.name}_{str(timezone.datetime.now().time()).replace(':', '.')}"
    with open(temp_file_name, 'wb+') as destination:
        for chunk in file.chunks():
            destination.write(chunk)

    contacts = build_contacts_from_csv(temp_file_name, is_user_contacts=is_user_contacts)

    if contacts == 'dialect_error':
        return False, contacts

    if is_user_contacts:
        user_list = List.objects.get(pk=list_id)
        user_list_containers = user_list.listcontainer_set
        containers = [ListContainer(list=user_list, contact=contact) for contact in contacts if
                      not user_list_containers.filter(contact=contact).exists()]
        ListContainer.objects.bulk_create(containers)

    os.remove(temp_file_name)

    return True, len(contacts)


def get_list_data(sending_mails_lists_ids, page: int = 1):
    list_analytics = dict()

    for sending_mails_list_id in sending_mails_lists_ids:
        emails = SendingMails.objects.filter(sendingmails_list_id=sending_mails_list_id).select_related(
            'sendingmails_list', 'recipient')
        telegram_mails = SendingTelegram.objects.filter(sendingmails_list_id=sending_mails_list_id).select_related(
            'sendingmails_list', 'recipient')

        pending_count = emails.filter(status='Pending').count() + telegram_mails.filter(status='Pending').count()
        delivered_count = emails.filter(status='Delivered').count() + telegram_mails.filter(status='Delivered').count()
        error_count = emails.filter(status__icontains='Error').count() + telegram_mails.filter(
            status__icontains='Error').count()
        opened_count = emails.filter(status__icontains='Opened').count()
        all_count = emails.count() + telegram_mails.count()
        cancelled_count = emails.filter(status='Cancelled').count() + telegram_mails.filter(status='Cancelled').count()

        sent_count = opened_count + delivered_count
        objects = list(emails) + list(telegram_mails)
        list_analytics[sending_mails_list_id] = get_paginated_queryset(objects,
                                                                       page=page), pending_count, delivered_count, error_count, opened_count, sent_count, all_count, cancelled_count, telegram_mails.exists()
    return list_analytics


def validate_file_extension(value):
    import os
    from django.core.exceptions import ValidationError
    ext = os.path.splitext(value.name)[1]
    valid_extensions = ['.csv']
    if not ext.lower() in valid_extensions:
        raise ValidationError(u'Unsupported file extension.')
