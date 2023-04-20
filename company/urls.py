from django.urls import path

from .views import *

urlpatterns = [
    path('', ContactsListView.as_view(), name='contacts_list'),
    path('<int:list_id>/', ContactsListView.as_view(), name='contacts_list'),
    
    path('contacts/', ContactView.as_view(), name='contacts'),
    path('contacts/<str:action>/', ContactView.as_view(), name='contacts'),
    path('<int:list_id>/contacts/', ContactView.as_view(), name='contacts'),
    path('<int:list_id>/contacts/<str:action>/', ContactView.as_view(), name='contacts'),

    path('contacts/actions/', ContactsActionsView.as_view(), name='contacts_actions'),

    path('company_name_autocomplete/', company_name_autocomplete, name='company_name_autocomplete'),
    path('company_info/', get_company_id_by_its_name, name='company_id_by_its_name'),
    path('company/get_contact_data/<uuid:contact_id>/', get_contact_data, name='get_contact_data'),

    path('delete_contact/', delete_contacts_list, name='delete_list'),
    path('generate_emails/', generate_mail, name='generate_emails'),
    path('add_contact_to_list/<uuid:contact_id>/', add_contact_to_list, name='add_contact_to_list'),
    path('operator_page/', operator_page, name='operator_page'),
    path('operator_page/<uuid:company_id>/', operator_page, name='operator_page'),
    path('init_operator_group/', create_operator_roles, name='init_operator'),

    path('get_current_variables_data/', get_current_variables_data, name='get_current_variables_data'),

    path('templates/', TempaltesListView.as_view(), name='templates'),
    path('templates/<int:list_id>/', TempaltesListView.as_view(), name='templates'),
    path('templates/<int:list_id>/template/', TemplateView.as_view(), name='template'),
    path('templates/<int:list_id>/template/<str:action>/', TemplateView.as_view(), name='template'),
    path('templates/actions/', TemplatesActionsView.as_view(), name='template_actions'),

    path('newsletters/', NewslettersListView.as_view(), name='newsletters'),
    path('newsletters/<int:list_id>/', NewslettersListView.as_view(), name='newsletters'),
    path('newsletters/<int:list_id>/newsletter/', NewsletterView.as_view(), name='newsletter'),
    path('newsletters/<int:list_id>/newsletter/<str:_for>/', NewsletterView.as_view(), name='newsletter'),
    path('newsletters/<int:list_id>/newsletter/<int:newsletter_id>/<str:_for>/', NewsletterView.as_view(), name='newsletter'),

    path('newsletters/actions/', NewslettersActionsView.as_view(), name='newsletters_actions'),

    path('templates/get_template_data/<int:template_id>/', get_template_data_by_id, name='get_template_data_by_id'),
    path('templates/get_email_popup_data/', get_email_popup_data, name='get_email_popup_data'),

    path('sendings/', SendingMailsListView.as_view(), name='sending_mails'),
    path('sendings/<int:list_id>/', SendingMailsListView.as_view(), name='sending_mails'),
    path('sendings/<int:list_id>/sending/', SendingMailsView.as_view(), name='sending_mail'),
    path('sendings/<int:list_id>/<str:_for>/', SendingMailsListView.as_view(), name='sending_mails'),
    path('sending_mails/<int:list_id>/start/', StartSendingMailsView.as_view(), name='sendingmails_start'),
    path('sending_mails/<int:list_id>/stop/', StopSendingMailsView.as_view(), name='sendingmails_stop'),
    path('sending_mails/actions/', SendingActionsView.as_view(), name='sending_mails_actions'),

    path('find-clients/', FindClientsView.as_view(), name='find_clients'),
    path('find-clients/<str:by>/', FindClientsView.as_view(), name='find_clients'),

    path('add_industry/', add_industry),
    path('export_list/<int:list_id>/', export_list_to_csv, name='export_list_to_csv'),

    path('get_client_data/',get_client_data,name="get_client_data"),
    path('get_company_data/<uuid:company_id>/',get_company_data,name="get_company_data"),

    path('open/<str:path>/', MyOpenTrackingView.as_view(), name="open_tracking"),
]
