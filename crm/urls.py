from django.urls import path

from . import views

urlpatterns = [
    path('', views.boards, name='boards'),
    path('<uuid:board_id>/', views.board, name='board'),
    path('<uuid:board_id>/edit/', views.board_edit_page, name='edit_board'),
    path('<uuid:board_id>/delete/', views.delete_board, name='delete_board'),
    path('<uuid:board_id>/contracts/create/', views.create_contract, name='create_contract'),
    path('<uuid:board_id>/contract/<uuid:contract_id>', views.contract, name='contract'),
    path('<uuid:board_id>/contracts/transfer/<uuid:contract_id>/', views.transfer_contract, name='transfer_contract'),
    path('<uuid:board_id>/contracts/to_trash/<uuid:contract_id>/', views.add_contract_to_trash,
         name='add_contract_to_trash'),

    path('accept_board_invite/<int:invite_id>/', views.accept_board_invite, name='accept_board_invite'),
    path('decline_board_invite/<int:invite_id>/', views.decline_board_invite, name='decline_board_invite'),
    path('<uuid:board_id>/contracts/delete/<uuid:contract_id>/', views.delete_contract, name='delete_contract'),
    path('<uuid:board_id>/statuses/edit/<uuid:status_id>/', views.edit_status, name='edit_status'),

    path('<uuid:board_id>/statuses/delete/<uuid:status_id>/', views.delete_status, name='delete_status'),
    path('board/remove_from_board/<int:permission_id>', views.delete_from_board, name='delete_from_board'),

    path('contracts/statistic/', views.contracts_statistic, name='contracts_statistic'),
    path('contracts_statistic/get_contracts_data/', views.get_contracts_data, name="get_contracts_data"),
    path('contracts_statistic/filter_contracts_data/', views.filter_contracts_data, name="filter_contracts_data"),
    path('contracts_statistic/update_stats_table/', views.update_stats_table, name="update_stats_table"),
    path('contracts/by_team_member/', views.contracts_by_teammember, name='contracts_by_teammember'),
    path('contracts/create_contact/', views.create_contact_from_contract, name='create_contact_from_contract'),
    path('contracts/change_contracts_contact/', views.change_contracts_contact, name='change_contracts_contact'),
    path('contract/delete_attachment/<uuid:contract_id>/', views.delete_attachment, name='delete_attachment'),

]
