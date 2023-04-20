import csv
import logging
import json
import pytz
from datetime import timedelta, datetime

from django.contrib.auth.decorators import permission_required, login_required
from django.db.models import Q, QuerySet
from transliterate import translit

from django.views import View
from django.utils import timezone
from django.urls import reverse
from django.contrib import messages
from django.http import JsonResponse, HttpResponse, HttpRequest
from django.shortcuts import render, redirect
from django.utils.translation import gettext_lazy, activate as activate_language

from pytracking import Configuration
from pytracking.django import OpenTrackingView

from company.forms import *
from company.models import *
from company.utils import *
from users.models import UserModel
from dashboard.models import *
from .pagination import get_paginated_queryset
from . import services as svc
from users.utils import get_client_ip

logger = logging.getLogger('user_events')


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


class ContactsListView(View):

    def get(self, request: HttpRequest, list_id: int | None = None):
        return svc.get_contacts(request, list_id)

    def post(self, request: HttpRequest):
        return svc.create_contacts_list(request)

    def patch(self, request: HttpRequest):
        return svc.update_contacts_list(request)

    def delete(self, request: HttpRequest):
        return svc.delete_contacts_list(request)


class ContactView(View):

    def get(self, request: HttpRequest, list_id: int):
        return svc.get_contacts_table(request, list_id)

    def post(self, request: HttpRequest, list_id: int | None = None, action: str | None = None):
        if action == 'create': return svc.create_contact(request, list_id)
        if action == 'email': return svc.get_contact_email(request)
        if action == 'search': return svc.contact_search(request) 
    
    def patch(self, request: HttpRequest, list_id: int, action: str):
        if action == 'edit': return svc.edit_contact(request, list_id)
        if action == 'transfer': return svc.transfer_contact(request, list_id)
        return HttpResponse()

    def delete(self, request: HttpRequest):
        return svc.delete_contact(request)


class ContactSearchView(View):

    def post(self, request: HttpRequest):
        return svc.contact_search(request)


class ContactsActionsView(View):

    def post(self, request: HttpRequest):
        return svc.contacts_actions(request)


def get_contact_data(request, contact_id):
    contact = UsersContacts.objects.get(pk=contact_id)

    data = {
        'name': contact.name,
        'surname': contact.surname,
        'middle_name': contact.middle_name,
        'email': contact.email,
        'phone': str(contact.phone),
        'company_name': contact.company.company_name,
        'company_site': contact.company.company_site,
        'position_in_company': contact.position_in_company,
        'telegram_id': contact.telegram_id
    }
    return JsonResponse(data, safe=False)


class TempaltesListView(View):

    def get(self, request: HttpRequest, list_id: int | None = None):
        return svc.get_templates(request, list_id)

    def post(self, request: HttpRequest):
        return svc.add_templates_list(request)
    
    def patch(self, request: HttpRequest):
        return svc.edit_templates_list(request)
    
    def delete(self, request: HttpRequest):
        return svc.delete_templates_list(request)


class TemplateView(View):

    def get(self, request: HttpRequest, list_id: int):
        return svc.get_templates_table(request, list_id)

    def post(self, request: HttpRequest, list_id: int):
        return svc.create_template(request, list_id)
    
    def patch(self, request: HttpRequest, list_id: int, action: str):
        if action == 'edit': return svc.edit_tempalte(request, list_id)
        if action == 'transfer': return svc.transfer_template(request, list_id)
        return HttpResponse()

    def delete(self, request: HttpRequest, list_id: int):
        return svc.delete_tempalte(request, list_id)

    
class TemplatesActionsView(View):

    def post(self, request: HttpRequest):
        return svc.templates_actions(request)


def get_templates_list_data(request, list_id: int):
    template_list: TemplatesList = TemplatesList.objects.get(pk=list_id)
    data = {
        'list_name': template_list.list_name
    }
    return JsonResponse(data, safe=False)


class NewslettersListView(View):

    def get(self, request: HttpRequest, list_id: int | None = None):
        return svc.get_newsletters(request, list_id)
    
    def post(self, request: HttpRequest):
        return svc.create_newsletters_list(request)
    
    def patch(self, request: HttpRequest, list_id: int):
        return svc.edit_newsletters_list(request, list_id)
    
    def delete(self, request: HttpRequest):
        return svc.delete_newsletters_list(request)


class NewsletterView(View):

    def get(self, request: HttpRequest, list_id: int, _for: str, newsletter_id: int | None = None):
        if _for == 'add': return svc.get_add_newsletter_template_page(request, list_id)
        if _for == 'edit': return svc.get_edit_newsletter_template_page(request, list_id, newsletter_id)
        if _for == 'table': return svc.get_newsletters_table(request, list_id)
        return HttpResponse()

    def post(self, request: HttpRequest, list_id: int, _for: str, newsletter_id: int | None = None):
        if _for == 'add': return svc.add_newsletter_template(request, list_id)
        if _for == 'edit': return svc.edit_newsletter_template(request, list_id, newsletter_id)
        return HttpResponse()
    
    def patch(self, request: HttpRequest, list_id: int):
        return svc.transfer_newsletter(request, list_id)

    def delete(self, request: HttpRequest, list_id: int):
        return svc.delete_newsletter(request, list_id)


class NewslettersActionsView(View):

    def post(self, request: HttpRequest):
        return svc.newsletters_actions(request)


def get_template_data_by_id(request, template_id):
    template = Template.objects.get(pk=template_id)
    data = {
        'subject_line': template.subject_line,
        'message': template.message
    }
    return JsonResponse(data)


def get_email_popup_data(request):
    data = request.POST.get('subject_line')
    return JsonResponse(data, safe=False)


class SendingMailsListView(View):

    def get(self, request: HttpRequest, list_id: int | None = None, _for: str | None = None):
        if _for == 'refresh': return svc.refresh_sending_page(request, list_id)
        if _for == 'table': return svc.get_sending_table(request, list_id)
        return svc.get_sending_mails(request, list_id)

    def post(self, request: HttpRequest):
        return svc.create_sending(request)
    
    def patch(self, request: HttpRequest, list_id: int):
        return svc.edit_sendings_list(request, list_id)
    
    def delete(self, request: HttpRequest):
        return svc.delete_sendings_list(request)


class SendingMailsView(View):

    def patch(self, request: HttpRequest, list_id: int):
        return svc.break_sending(request, list_id)
    
    def delete(self, request: HttpRequest, list_id: int):
        return svc.delete_sending(request, list_id)


class StartSendingMailsView(View):

    def post(self, request: HttpRequest, list_id: int):
        return svc.start_sendingmails(request, list_id)
    

class StopSendingMailsView(View):

    def post(self, request: HttpRequest, list_id: int):
        return svc.stop_sendingmails(request, list_id)


class SendingActionsView(View):

    def post(self, request: HttpRequest):
        return svc.sending_actions(request)
    

class FindClientsView(View):

    def get(self, request: HttpRequest):
        return svc.find_clients_page(request)
    
    def post(self, request: HttpRequest, by: str):
        if by == 'name': return svc.find_clients_by_name(request)
        if by == 'domain': return svc.find_clients_by_domain(request)
        if by == 'feature': return svc.find_clients_by_feature(request)
        return HttpResponse()


def delete_contacts_list(request):
    if request.method == "POST":
        data = json.loads(request.body.decode('utf-8'))
        ids_to_delete = list(map(int, data['ids_to_delete']))
        containers = ListContainer.objects.filter(
            id__in=ids_to_delete).filter(list__list_owner=request.user)
        logger.info(f"Deleting containers: {containers}")
        containers.delete()

    return HttpResponse()


def company_name_autocomplete(request):
    if request.GET:
        q = request.GET.get('q')
        data = ContactCompany.objects.filter(
            company_name__startswith=q).values_list('company_name', flat=True)
        json = list(data)
        return JsonResponse(json, safe=False)
    return JsonResponse("test", safe=False)


def get_company_id_by_its_name(request):
    if request.GET:
        name = request.GET.get('company_name')
        try:
            data = ContactCompany.objects.get(company_name__exact=name)
        except ContactCompany.DoesNotExist as e:
            return JsonResponse({"id": None, "url": None})
        return JsonResponse({"id": data.id, "url": data.company_site})


def generate_mail(request):
    if request.method == 'GET':
        first_name, surname, domain = request.GET.get(
            "first_name"), request.GET.get("surname"), request.GET.get(
            "domain")
        trans_name = translit(first_name, language_code='ru', reversed=True)
        trans_surname = translit(surname, language_code='ru', reversed=True)

        return JsonResponse(
            {'emails': [email for email, status in
                        dict(get_emails_new(trans_name, trans_surname, domain)).items() if
                        status]})


def get_current_variables_data(request):
    variables = [{variable.name: variable.variable}
                 for variable in UserLocalVariable.objects.all()]
    return JsonResponse(variables, safe=False)


def add_industry(request):
    if request.GET.get('id') == 'rimsol':
        try:
            industries_success = False
            if len(CompanyBranch.objects.all()) == 0:
                try:
                    industries_en = ['Accounting',
                                     'Administrative',
                                     'Agriculture',
                                     'Airlines/Aviation',
                                     'Alternative dispute resolution',
                                     'Alternative medicine',
                                     'Animation',
                                     'Apparel & Fashion',
                                     'Architecture & Planning',
                                     'Arts & Crafts',
                                     'Automotive',
                                     'Aviation & Aerospace',
                                     'Banking',
                                     'Biotechnology',
                                     'Broadcast media',
                                     'Building materials',
                                     'Business supplies & Equipment',
                                     'Capital markets',
                                     'Chemicals',
                                     'Civic & Social organization',
                                     'Civil engineering',
                                     'Commercial real estate',
                                     'Computer & Network security',
                                     'Computer games',
                                     'Computer hardware',
                                     'Computer networking',
                                     'Computer software',
                                     'Construction',
                                     'Consulting',
                                     'Consumer electronics',
                                     'Consumer goods',
                                     'Consumer services',
                                     'Cosmetics',
                                     'Dairy',
                                     'Defense & Space',
                                     'Design',
                                     'E-learning',
                                     'Education',
                                     'Education management',
                                     'Electrical/Electronic manufacturing',
                                     'Engineering',
                                     'Entertainment',
                                     'Entrepreneurship',
                                     'Environmental services & Clean energy',
                                     'Events services',
                                     'Executive office',
                                     'Facilities & Services',
                                     'Farming',
                                     'Finance',
                                     'Financial services',
                                     'Fine art',
                                     'Fishery',
                                     'Food & Beverages',
                                     'Food production',
                                     'Fund-raising',
                                     'Furniture',
                                     'Gambling & Casinos',
                                     'Glass, ceramics & Concrete',
                                     'Government administration',
                                     'Government relations',
                                     'Graphic design',
                                     'Health, Wellness & Fitness',
                                     'Higher education',
                                     'Hospital & Health care',
                                     'Hospitality',
                                     'Human resources',
                                     'Import & Export',
                                     'Individual & Family services',
                                     'Industrial automation',
                                     'Information services',
                                     'Information technology & Services',
                                     'Insurance',
                                     'International affairs',
                                     'International trade & Development',
                                     'Internet',
                                     'Investment banking/Venture',
                                     'Investment management',
                                     'Judiciary',
                                     'Law enforcement',
                                     'Law practice',
                                     'Legal',
                                     'Legal services',
                                     'Legislative office',
                                     'Leisure, Travel & Tourism',
                                     'Libraries',
                                     'Logistics & Supply chain',
                                     'Luxury goods & Jewelry',
                                     'Machinery',
                                     'Management consulting',
                                     'Manufacturing',
                                     'Maritime',
                                     'Market research',
                                     'Marketing',
                                     'Marketing & Advertising',
                                     'Mechanical or Industrial engineering',
                                     'Media production',
                                     'Medical devices',
                                     'Medical practice',
                                     'Mental health care',
                                     'Military',
                                     'Mining & Metals',
                                     'Motion pictures & Film',
                                     'Museums & Institutions',
                                     'Music',
                                     'Nanotechnology',
                                     'Newspapers',
                                     'Non-profits & Non-profit services',
                                     'Oil & Energy',
                                     'Online media',
                                     'Online publishing',
                                     'Operations',
                                     'Outsourcing/Offshoring',
                                     'Package/Freight delivery',
                                     'Packaging & Containers',
                                     'Paper & Forest products',
                                     'Performing arts',
                                     'Pharmaceuticals',
                                     'Philanthropy',
                                     'Photography',
                                     'Plastics',
                                     'Political organization',
                                     'Primary/Secondary education',
                                     'Printing',
                                     'Professional training & Coaching',
                                     'Program development',
                                     'Public policy',
                                     'Public relations & Communications',
                                     'Public safety',
                                     'Publishing',
                                     'Railroad manufacture',
                                     'Ranching',
                                     'Real estate',
                                     'Recreational facilities & Services',
                                     'Religious institutions',
                                     'Renewables & Environment',
                                     'Research',
                                     'Restaurants',
                                     'Retail',
                                     'Sales',
                                     'Security & Investigations',
                                     'Semiconductors',
                                     'Shipbuilding',
                                     'Sporting goods',
                                     'Sports',
                                     'Staffing & Recruiting',
                                     'Supermarkets',
                                     'Support',
                                     'Telecommunications',
                                     'Textiles',
                                     'Think tanks',
                                     'Tobacco',
                                     'Translation & Localization',
                                     'Transportation',
                                     'Transportation/Trucking/railroad',
                                     'Utilities',
                                     'Venture capital & Private equity',
                                     'Veterinary',
                                     'Warehousing',
                                     'Wholesale',
                                     'Wine & Spirits',
                                     'Wireless',
                                     'Writing & Editing']
                    industries_ru = ["Бухгалтерский учет",
                                     "Административное управление",
                                     "Сельское хозяйство",
                                     "Авиалинии/Авиация",
                                     "Альтернативное разрешение споров",
                                     "Альтернативная медицина",
                                     "Анимация",
                                     "Одежда и мода",
                                     "Архитектура и планирование",
                                     "Искусство и ремесла",
                                     "Автомобилестроение",
                                     "Авиация и аэрокосмическая промышленность",
                                     "Банковское дело",
                                     "Биотехнология",
                                     "Средства массовой информации",
                                     "Строительные материалы",
                                     "Товары и оборудование для бизнеса",
                                     "Рынки капитала",
                                     "Химикаты",
                                     "Гражданские и общественные организации",
                                     "Гражданское строительство",
                                     "Коммерческая недвижимость",
                                     "Компьютерная и сетевая безопасность",
                                     "Компьютерные игры",
                                     "Компьютерное оборудование",
                                     "Компьютерные сети",
                                     "Компьютерное программное обеспечение",
                                     "Строительство",
                                     "Консалтинг",
                                     "Бытовая электроника",
                                     "Товары народного потребления",
                                     "Бытовые услуги",
                                     "Косметика",
                                     "Молочные продукты",
                                     "Оборона и космос",
                                     "Дизайн",
                                     "Электронное обучение",
                                     "Образование",
                                     "Управление образованием",
                                     "Производство электротехники и электроники",
                                     "Инженерное дело",
                                     "Развлечения",
                                     "Предпринимательство",
                                     "Экологические услуги и чистая энергия",
                                     "Услуги по организации мероприятий",
                                     "Исполнительный офис",
                                     "Объекты и услуги",
                                     "Сельское хозяйство",
                                     "Финансы",
                                     "Финансовые услуги",
                                     "Изобразительное искусство",
                                     "Рыболовство",
                                     "Продукты питания и напитки",
                                     "Производство продуктов питания",
                                     "Сбор средств",
                                     "Мебель",
                                     "Азартные игры и казино",
                                     "Стекло, керамика и бетон",
                                     "Государственное управление",
                                     "Отношения с правительством",
                                     "Графический дизайн",
                                     "Здоровье, хорошее самочувствие и фитнес",
                                     "Высшее образование",
                                     "Больницы и здравоохранение",
                                     "Гостиничный бизнес",
                                     "Человеческие ресурсы",
                                     "Импорт и экспорт",
                                     "Индивидуальные и семейные услуги",
                                     "Промышленная автоматизация",
                                     "Информационные услуги",
                                     "Информационные технологии и услуги",
                                     'Страхование',
                                     "Международные отношения",
                                     "Международная торговля и развитие",
                                     "Интернет",
                                     "Инвестиционное банковское дело /Венчурное предприятие",
                                     "Управление инвестициями",
                                     "Судебная власть",
                                     "Правоохранительные органы",
                                     "Юридическая практика",
                                     "Юриспруденция",
                                     "Юридические услуги",
                                     "Законодательный орган",
                                     "Досуг, путешествия и туризм",
                                     "Библиотеки",
                                     "Логистика и цепочки поставок",
                                     'Предметы роскоши и ювелирные изделия',
                                     "Оборудование",
                                     "Управленческий консалтинг",
                                     "Производство",
                                     "Морское дело",
                                     "Маркетинговые исследования",
                                     "Маркетинг",
                                     "Маркетинг и реклама",
                                     "Машиностроение или промышленное машиностроение",
                                     "Медиапроизводство",
                                     "Медицинское оборудование",
                                     "Медицинская практика",
                                     "Психиатрическая помощь",
                                     "Военные",
                                     "Горнодобывающая промышленность и металлургия",
                                     "Кино и кино",
                                     "Музеи и учреждения",
                                     "Музыка",
                                     "Нанотехнологии",
                                     "Газеты",
                                     "Некоммерческие организации и некоммерческие услуги",
                                     "Нефть и энергетика",
                                     "Онлайн-СМИ",
                                     "Онлайн-публикации",
                                     "Операции",
                                     "Аутсорсинг/Офшоринг",
                                     "Доставка посылок/грузов",
                                     "Упаковка и контейнеры",
                                     "Бумага и лесная продукция",
                                     "Исполнительское искусство",
                                     "Фармацевтика",
                                     "Филантропия",
                                     "Фотография",
                                     "Пластмассы",
                                     "Политическая организация",
                                     "Начальное/среднее образование",
                                     "Печать",
                                     "Профессиональное обучение и коучинг",
                                     "Разработка программ",
                                     "Государственная политика",
                                     "Связи с общественностью и коммуникации",
                                     "Общественная безопасность",
                                     "Издательская деятельность",
                                     "Производство железных дорог",
                                     "Скотоводство",
                                     "Недвижимость",
                                     "Объекты отдыха и услуги",
                                     "Религиозные учреждения",
                                     "Возобновляемые источники энергии и окружающая среда",
                                     "Исследования",
                                     "Рестораны",
                                     "Розничная торговля",
                                     "Продажи",
                                     "Безопасность и расследования",
                                     "Полупроводники",
                                     "Судостроение",
                                     "Спортивные товары",
                                     "Спорт",
                                     "Подбор персонала и рекрутинг",
                                     "Супермаркеты",
                                     "Поддержка",
                                     "Телекоммуникации",
                                     "Текстиль",
                                     "Аналитические центры",
                                     "Табак",
                                     "Перевод и локализация",
                                     "Транспорт",
                                     "Транспорт /Грузоперевозки /железная дорога",
                                     "Коммунальные услуги",
                                     "Венчурный капитал и частные инвестиции",
                                     "Ветеринария",
                                     "Складирование",
                                     "Оптовая торговля",
                                     "Вино и спиртные напитки",
                                     "Беспроводная связь",
                                     "Написание и редактирование"]
                    industries: list[CompanyBranch] = [CompanyBranch(
                        industry_en=industries_en[i], industry_ru=industries_ru[i]) for i in range(len(industries_ru))]
                    CompanyBranch.objects.bulk_create(industries)
                    industries_success = True
                except Exception as e:
                    industries_success = False
                    print(e)

            sizes_success = False
            if len(CompanySizes.objects.all()) == 0:
                try:
                    sizes = [CompanySizes(size='1-10'), CompanySizes(size='10-50'), CompanySizes(size='50-100'),
                             CompanySizes(
                                 size='100-250'), CompanySizes(size='250 - 500'), CompanySizes(size='500-1000'),
                             CompanySizes(size='1000>')]
                    CompanySizes.objects.bulk_create(sizes)
                    sizes_success = True
                except:
                    sizes_success = False

            variables_success = False
            if len(UserLocalVariable.objects.all()) == 0:
                try:
                    variables = [UserLocalVariable(name_en='Surname', name_ru='Фамилия', variable='surname'),
                                 UserLocalVariable(
                                     name_en='Name', name_ru='Имя', variable='name'),
                                 UserLocalVariable(
                                     name_en='Middlename', name_ru='Отчество', variable='middlename'),
                                 UserLocalVariable(
                                     name_en='Email', name_ru='Email', variable='email'),
                                 UserLocalVariable(
                                     name_en='Phone', name_ru='телефон', variable='phone_number'),
                                 UserLocalVariable(name_en='Company name', name_ru='Название компании',
                                                   variable='company_name'),
                                 UserLocalVariable(name_en='Company site', name_ru='Сайт компании',
                                                   variable='company_site'),
                                 UserLocalVariable(name_en='Position', name_ru='Должность ', variable='position')]
                    UserLocalVariable.objects.bulk_create(variables)
                    variables_success = True
                except:
                    variables_success = False

            return JsonResponse({'success': True, 'industries': industries_success, 'sizes': sizes_success,
                                 'variables': variables_success})
        except:
            return JsonResponse({'success': False, 'industries': False, 'sizes': False, 'variables': False})
    else:
        return JsonResponse({'success': False, 'industries': False, 'sizes': False, 'variables': False})


@login_required
def export_list_to_csv(request, list_id):
    if request.method == 'GET':
        if not List.objects.filter(pk=list_id).exists():
            return JsonResponse({'success': False, 'message': 'List not found'})
        requested_list = List.objects.get(pk=list_id)
        if requested_list.list_owner != request.user:
            return JsonResponse({'success': False, 'reason': 'You are not owner of this list'})

        response = HttpResponse(content_type='text/csv;')
        response[
            'Content-Disposition'] = f'attachment; filename="salestech_export_list_{list_id}.csv"'
        response.write(u'\ufeff'.encode('utf8'))
        writer = csv.writer(response)
        writer.writerow(
            ['Last name', 'First name', 'Middle name', 'Email', 'Phone number', 'Company name', 'Company url',
             'Job position', 'Company industry', 'Company size'])
        for container in requested_list.listcontainer_set.all():
            writer.writerow([container.contact.surname, container.contact.name, container.contact.middle_name,
                             container.contact.email, container.contact.phone, container.contact.company.company_name,
                             container.contact.company.company_site, container.contact.position_in_company,
                             container.contact.company.company_branch.industry_en if container.contact.company.company_branch else '',
                             container.contact.company.company_size.size if container.contact.company.company_size else ''])
        return response
    else:
        return HttpResponse('Invalid request method. Use GET')


def add_contact_to_list(request, contact_id: int):
    if request.method == 'POST':
        add_contact_to_existing_list = AddContactToExistingList(
            request.POST, request=request)
        if add_contact_to_existing_list.is_valid():
            selected_list = add_contact_to_existing_list.cleaned_data.get(
                'user_lists')
            contact = Contact.objects.get(pk=contact_id)
            container = ListContainer.objects.create(
                list=selected_list, contact=contact)
            container.save()
    return redirect(reverse('contacts_list'))


@permission_required('company.access_operator_interface')
def operator_page(request, company_id: int | None = None):
    page = request.GET.get('page', 1)

    selected_size = None
    selected_industry = None

    search_form = OperatorBranchSearch()
    add_contact_form = AddContactForm()
    add_contacts_from_file_form = AddContactsFromFileForm()

    all_companies = ContactCompany.objects.select_related('company_branch', 'company_size').filter(
        Q(company_branch=None) | Q(company_size=None))
    all_contacts = Contact.objects.all()

    if request.method == 'POST':

        if 'first_name' in request.POST.keys():
            form = AddContactForm(request.POST)

            if form.is_valid():
                data = form.data
                if data['site']:
                    # Находим в БД или создаем компанию по ее урлу
                    company_for_contact, created = ContactCompany.objects.get_or_create(
                        # company_name__iexact=data['company'], # в принципе ненужный функционал,
                        # т.к. имя компании будет задаваться единожды
                        company_site__iexact=data['site'],
                        defaults={'company_name': data['company'],
                                  'company_site': data['site']})
                else:
                    company_for_contact, created = ContactCompany.objects.get_or_create(
                        # в принципе ненужный функционал,
                        company_name__iexact=data['company'],
                        # т.к. имя компании будет задаваться единожды
                        company_site__iexact=data['site'],
                        defaults={'company_name': data['company'],
                                  'company_site': data['site']})

                if company_for_contact.company_name == "":  # если имя компании не задано при создании
                    company_for_contact.company_name = data['company']

                created_contact: Contact = Contact(name=data['first_name'], surname=data['surname'],
                                                   middle_name=data['middle_name'],
                                                   phone=data['phone_number'],
                                                   position_in_company=data['position'],
                                                   email=data['email'],
                                                   company=company_for_contact)
                company_for_contact.save()
                created_contact.save()

                request.user.company.save()

                logger.info('SUCCESS ADD CLIENT', extra={
                    'user_ip': get_client_ip(request), 'user_email': request.user.email})

            else:
                for field in form:
                    for error in field.errors:
                        current_error = error

                print([error for form in field.errors for field in form])
                messages.add_message(request, messages.ERROR, current_error)

            return redirect(f"{reverse('operator_page')}?page={page}#contacts")

        elif 'file' in request.FILES.keys():
            uploaded_file_form = AddContactsFromFileForm(request.POST, request.FILES)

            if uploaded_file_form.is_valid():
                try:
                    result, contacts = handle_uploaded_csv(request.FILES['file'], request.user, is_user_contacts=False)
                    if not result:
                        if contacts == 'dialect_error':
                            messages.add_message(request, messages.ERROR, gettext_lazy(
                                'Error! The file must contain one of the delimiters: ";" or ","'))
                    else:
                        messages.add_message(request, messages.SUCCESS,
                                             gettext_lazy('Added ') + contacts + gettext_lazy(' contacts'))
                except Exception as e:
                    messages.add_message(request, messages.ERROR, gettext_lazy('Please enter a valid file'))
            else:
                messages.error(request, gettext_lazy('Invalid file!'))
            return redirect(f"{reverse('operator_page')}?page={page}#contacts")

        if company_id is None:
            all_companies = ContactCompany.objects.all().select_related(
                'company_branch', 'company_size')
            selected_industry_id, selected_size_id = request.POST[
                'industry'], request.POST['company_size']

            if selected_size_id:
                selected_size = int(selected_size_id)
                all_companies = all_companies.filter(
                    company_size=CompanySizes.objects.get(pk=int(selected_size_id)))
            if selected_industry_id:
                selected_industry = int(selected_industry_id)
                all_companies = all_companies.filter(
                    company_branch=CompanyBranch.objects.get(pk=int(selected_industry_id)))

        else:
            company_to_change = ContactCompany.objects.get(pk=company_id)

            company_to_change.company_name, company_to_change.company_site = request.POST[
                'company_name'], request.POST['company_site'],

            company_to_change.company_branch = CompanyBranch.objects.get(
                pk=int(request.POST['company_branch']))

            company_to_change.company_size = CompanySizes.objects.get(
                pk=int(request.POST['company_size']))
            company_to_change.save()

            return redirect(f"{reverse('operator_page')}?page={page}")

    companies_paginator = get_paginated_queryset(all_companies, page=page)
    contacts_paginator = get_paginated_queryset(all_contacts, page=page)

    return render(request, 'company/operator_page.html', {'search_form': search_form,
                                                          'companies_paginator': companies_paginator,
                                                          'contacts_paginator': contacts_paginator,
                                                          'selected_size': selected_size,
                                                          'selected_industry': selected_industry,
                                                          'add_contact_form': add_contact_form,
                                                          'add_contacts_from_file_form': add_contacts_from_file_form})


@login_required
def create_operator_roles(request):
    if request.user.is_superuser:
        from django.contrib.auth.models import Group, Permission
        from django.contrib.contenttypes.models import ContentType
        from company.models import CompanyBranch

        operator_permission, _permission_created = Permission.objects.get_or_create(
            codename='access_operator_interface',
            name='Access operator interface',
            content_type=ContentType.objects.get_for_model(
                CompanyBranch))
        operator_group, _group_created = Group.objects.get_or_create(
            name='operator')
        operator_group.permissions.add(operator_permission)
        operator_group.save()
        return JsonResponse({'_permission_created': _permission_created, 'operator_group_created': _group_created,
                             'operator_group_has_permission': operator_permission in operator_group.permissions.get_queryset(),
                             'group': f'Group(name={operator_group.name}, perms={operator_group.permissions})',
                             'permission': f'Permission(codename={operator_permission.codename})'})


def get_client_data(request):
    if request.method == 'POST':
        data = request.POST
        user_list = data['user_lists']
        first_name = data['first_name']
        surname = data['surname']
        middle_name = data['middle_name']
        email = data['email']
        phone_number = data['phone_number']
        position = data['position']
        company = data['company']
        site = data['site']

        # Находим в БД или создаем компанию по ее урлу
        company_for_contact, created = ContactCompany.objects.get_or_create(
            # company_name__iexact=data['company'], # в принципе ненужный функционал,
            # т.к. имя компании будет задаваться единожды
            company_site__iexact=site,
            defaults={'company_name': company,
                      'company_site': site})

        if company_for_contact.company_name == "":  # если имя компании не задано при создании
            company_for_contact.company_name = company

        list_where_we_add_data: List = List.objects.get(pk=int(user_list))

        user_created_contact: UsersContacts = UsersContacts(name=first_name,
                                                            surname=surname,
                                                            middle_name=middle_name,
                                                            phone=phone_number,
                                                            position_in_company=position,
                                                            email=email,
                                                            company=company_for_contact)

        container: ListContainer = ListContainer(
            list=list_where_we_add_data, contact=user_created_contact)
        company_for_contact.save()
        user_created_contact.save()
        container.save()

        request.user.company.save()

        logger.info('SUCCESS ADD CLIENT', extra={
            'user_ip': get_client_ip(request), 'user_email': request.user.email})

    return redirect("home")


def get_company_data(request, company_id):
    if request.method == "POST":
        data = request.POST
        company_name = data['company_name']
        company_site = data['company_site']
        company_branch = data['company_branch']
        company_size = data['company_size']

        company_to_change = ContactCompany.objects.get(pk=company_id)

        company_to_change.company_name, company_to_change.company_site = company_name, company_site

        company_to_change.company_branch = CompanyBranch.objects.get(
            pk=int(company_branch))

        company_to_change.company_size = CompanySizes.objects.get(
            pk=int(company_size))

        company_to_change.save()

    return redirect("home")


class MyOpenTrackingView(OpenTrackingView):

    def notify_tracking_event(self, tracking_result):
        # Override this method to do something with the tracking result.
        # tracking_result.request_data["user_agent"] and
        # tracking_result.request_data["user_ip"] contains the user agent
        # and ip of the client.

        if SendingMails.objects.filter(pk=tracking_result.metadata['email_id']).exists():
            current_email = SendingMails.objects.get(
                pk=tracking_result.metadata['email_id'])

            if timezone.now() - current_email.date > timedelta(seconds=60):  # проверка на самооткрытие письма
                current_email.opened_at = timezone.now()
                current_email.status = "Opened"
                current_email.opened_at_visual = f'({(current_email.opened_at).strftime("%b %d %Y %H:%M:%S")})'
                current_email.save()

    def notify_decoding_error(self, exception, request):
        # Called when the tracking link cannot be decoded
        # Override this to, for example, log the exception
        logger.log(exception)

    def get_configuration(self):
        # By defaut, fetchs the configuration parameters from the Django
        # settings. You can return your own Configuration object here if
        # you do not want to use Django settings.
        return Configuration()
