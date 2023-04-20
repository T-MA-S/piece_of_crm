import requests
import xmltodict
import datetime
import numpy as np
from uuid import UUID

from django.contrib import messages
from django.core.files.storage import get_storage_class
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.db.models import QuerySet, F
from django.db import transaction
from django.http import HttpRequest
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext
from django.utils.safestring import mark_safe

from company.forms import AddContactForm
from company.models import UsersContacts, ListContainer, List, ContactCompany, Notification
from users.models import UserModel
from .choices import ContractStatusColorChoices
from .forms import ContractEditForm, ContractEditFormNonOwner, ChangeBoardRole, EditBoardName
from .models import ContractLog, ContractFile, BoardPermissions, BoardInvite, BoardLog
from .models import ContractStatus, Contract, Board
from .models import Currency
from .utils import save_contract_file_in_bucket, set_statuses, get_member_stats


def boards(request: HttpRequest):
    user: UserModel = request.user
    if request.method == 'GET':
        boards_user_owns: dict[Board: dict[str: int]] = {board: {'members': board.boardpermissions_set.count(),
                                                                 'contracts': np.sum(
                                                                     [status.contract_set.count() for status in
                                                                      board.contractstatus_set.all()])} for board in
                                                         Board.get_user_owns_boards(user)}
        boards_user_guest: dict[Board: dict[str: int]] = {board: {'members': board.boardpermissions_set.count(),
                                                                  'contracts': np.sum(
                                                                      [status.contract_set.count() for status in
                                                                       board.contractstatus_set.all()])} for board in
                                                          Board.get_user_non_owns_boards(user)}

        user_invites_to_boards = BoardInvite.objects.filter(user=user,
                                                            status=BoardInvite.PENDING)

        context = {
            'boards_user_owns': boards_user_owns,
            'boards_user_guest': boards_user_guest,
            'user_invites_to_boards': user_invites_to_boards
        }
        return render(request, 'crm/boards_page.html', context=context)
    if request.method == 'POST':
        board_name, board_type = request.POST.get('name'), request.POST.get('board_type')
        if board_name:
            created_board = Board.objects.create(name=board_name)
            BoardPermissions.objects.create(board=created_board, user=user, role=BoardPermissions.OWNER)
            set_statuses(created_board.pk, board_type)
        return redirect('boards')


def board(request: HttpRequest, board_id: UUID):
    user: UserModel = request.user

    if request.method not in ['POST', 'GET']:
        messages.error(request, gettext('Invalid request method'))
        return redirect('boards')

    if not Board.objects.filter(id=board_id).exists():
        messages.error(request, gettext('Board not found'))
        return redirect('boards')

    board = Board.objects.get(pk=board_id)
    board_permission = board.get_permissions_for_user(user)

    if not board_permission:
        messages.error(request, gettext('You do not have access to this board'))
        return redirect('boards')

    if request.method == 'GET':

        board_members = user.company.members.all()
        statuses = board.contractstatus_set.exclude(
            name_ru='Удалена') if board_permission.role == BoardPermissions.EMPLOYEE else board.contractstatus_set.all()
        colors = ContractStatusColorChoices.choices

        add_contact_form = AddContactForm()

        currencies = Currency.objects.all()
        curr_list = ["RUB", "USD", "EUR", "AZN", "AMD", "BYN",
                     "KZT", "KGS", "CNY", "MDL", "TJS", "TMT", "UZS", "UAH"]
        ordered_currencies = [currencies.get(name=curr) for curr in curr_list]

        contacts = UsersContacts.objects.filter(
            pk__in=ListContainer.objects.filter(list__list_owner=user).values_list('contact', flat=True))

        data = {
            status: status.contract_set.filter(board_member__company=user.company) if board_permission.role in [
                BoardPermissions.OWNER, BoardPermissions.ADMIN] else status.contract_set.filter(
                board_member=request.user) if board_permission.role == BoardPermissions.EMPLOYEE else Contract.objects.none()
            for status in statuses
        }

        status_max_position = statuses.count()
        logs = board.retrieve_board_logs(user)

        context = {
            'board_id': board_id,
            'member_role': board_permission.role,
            'data': data,
            'currencies': ordered_currencies,
            'contacts': contacts,
            'board_members': board_members,
            'colors': colors,
            'add_contact_form': add_contact_form,
            'status_max_position': status_max_position,
            'logs': logs

        }

        return render(request, 'crm/board.html', context=context)

    else:
        name, color, position = request.POST.get('name'), request.POST.get('color'), request.POST.get('position')
        ContractStatus.objects.filter(board_id=board_id, position__gte=position).update(position=F('position') + 1)
        created_status = ContractStatus.objects.create(board_id=board_id, name=name, color=color, position=position)

        board.log_action(user, BoardLog.STATUS_ADDED_ACTION,
                         description=f"Пользователь {user.email} добавил статус {created_status.name}")

        return redirect('board', board_id=board_id)


def delete_from_board(request: HttpRequest, permission_id: int):
    if not (board_permission_object := BoardPermissions.objects.filter(pk=permission_id)).first():
        messages.error(request, gettext("Board not found"))
        return JsonResponse({"status": "error", "message": "Board does not exist"}, status=404)
    board_permission_object = board_permission_object.first()
    if not board_permission_object.board.get_owner() == request.user:
        messages.error(request, gettext("You do not have access to this board settings"))
        return JsonResponse({"status": "error", "message": "You do not have access to this board settings"}, status=403)
    if board_permission_object.user == request.user:
        messages.error(request, gettext("You can't remove yourself from board"))
        return JsonResponse({"status": "error", "message": "You can't remove yourself from team"}, status=400)
    board_permission_object.delete()
    messages.success(request, gettext("Successfully deleted member from board"))
    return JsonResponse({"status": "ok", "message": "user successfully deleted"})


def board_edit_page(request: HttpRequest, board_id: UUID):
    from dashboard.forms import InviteToTeamForm

    if not Board.objects.filter(id=board_id).exists():
        messages.error(request, gettext('Board not found'))
        return redirect('boards')

    user: UserModel = request.user
    board: Board = Board.objects.get(id=board_id)

    if not board.can_manage_board(user):
        messages.error(request, gettext('You do not have permission to edit this board'))
        return redirect('boards')

    can_invite_members: bool = board.can_user_invite_members(user)
    can_edit_role: bool = board.can_edit_role(user)
    current_user_permissions: BoardPermissions = board.get_permissions_for_user(user)

    if request.method == 'GET':
        # Реюзинг формы приглашения в команду для приглашений в борду
        invite_to_board_form = InviteToTeamForm()
        edit_board_name = EditBoardName(initial={'name': board.name})

        board_permissions: QuerySet[BoardPermissions] = board.get_board_members_permissions()
        board_invites: QuerySet[BoardInvite] = board.get_board_invites()

        permissions_to_roles = {
            permission: ChangeBoardRole(permission_id=permission.id) for permission in board_permissions
        }

        context = {
            'board': board,
            'board_permissions': board_permissions,
            'can_invite_members': can_invite_members,
            'can_edit_role': can_edit_role,
            'invite_to_board_form': invite_to_board_form,
            'board_invites': board_invites,
            'current_user_permissions': current_user_permissions,
            'permissions_to_roles': permissions_to_roles,
            'edit_board_name': edit_board_name
        }

        return render(request, 'crm/board_edit_page.html', context=context)

    if request.method == 'POST':
        invite_to_board_form = InviteToTeamForm(request.POST)
        change_board_member_role = ChangeBoardRole(request.POST)
        edit_board_name = EditBoardName(request.POST)
        if invite_to_board_form.is_valid():
            email = invite_to_board_form.cleaned_data['email']

            if not (invited_user := UserModel.objects.filter(email=email).first()):
                messages.error(request, gettext('User not found'))
                return redirect('edit_board', board_id=board_id)

            if board.get_permissions_for_user(invited_user):
                messages.error(request, gettext('User already added to this board'))
                return redirect('edit_board', board_id=board_id)

            board.invite_user(invited_user)
            messages.success(request, gettext('User invited'))
            Notification.objects.create(receiver=invited_user, text_ru=f'{user.email} пригласил вас к доске',
                                        text_en=f'{user.email} invited you to the board',
                                        redirect_url=reverse('board', kwargs={'board_id': board_id}))
        elif change_board_member_role.is_valid():
            if not can_edit_role:
                messages.error(request, gettext("You can't change roles in this board"))
                return redirect('board', board_id=board_id)
            permission_id = change_board_member_role.cleaned_data.get('permission_id')
            role = change_board_member_role.cleaned_data.get('role')
            permission_object = BoardPermissions.objects.get(pk=permission_id)
            permission_object.role = role
            permission_object.save()
            messages.success(request, gettext("Successfully changed role"))
            return redirect('edit_board', board_id=board_id)
        elif edit_board_name.is_valid():
            board.name = edit_board_name.cleaned_data.get('name')
            board.save()
            messages.success(request, gettext("Successfully changed board name"))
            return redirect('edit_board', board_id=board_id)


        else:
            messages.error(request, gettext('Invalid form data'))

        return redirect('edit_board', board_id=board_id)


def accept_board_invite(request, invite_id):
    if not BoardInvite.objects.filter(pk=invite_id).exists():
        messages.error(request, gettext('Invite not found'))
        return redirect('boards')
    if (invite_object := BoardInvite.objects.get(pk=invite_id)).user != request.user:
        messages.error(request, gettext('You do not have access to this invite'))
        return redirect('boards')
    if invite_object.status != BoardInvite.PENDING:
        messages.error(request, gettext('Invite already accepted or declined'))
        return redirect('boards')
    invite_object.accept_invite()
    messages.success(request, gettext('Successfully accepted invite'))
    return redirect('board', board_id=invite_object.board.id)


def decline_board_invite(request, invite_id):
    if not BoardInvite.objects.filter(pk=invite_id).exists():
        messages.error(request, gettext('Invite not found'))
        return redirect('boards')
    if (invite_object := BoardInvite.objects.get(pk=invite_id)).user != request.user:
        messages.error(request, gettext('You do not have access to this invite'))
        return redirect('boards')
    if invite_object.status != BoardInvite.PENDING:
        messages.error(request, gettext('Invite already accepted or declined'))
        return redirect('boards')
    invite_object.decline_invite()
    messages.success(request, gettext('Successfully declined invite'))
    return redirect('boards')


def edit_status(request: HttpRequest, board_id: UUID, status_id: UUID):
    if request.method != 'POST':
        messages.add_message(request, messages.ERROR, gettext('Invalid request method'))
        return redirect('boards')

    data = request.POST

    with transaction.atomic():
        if not Board.objects.filter(id=board_id).exists():
            messages.error(request, gettext('Board not found'))
            return redirect('boards')

        name, color, position = data.get('name'), data.get('color'), int(data.get('position'))

        if not ContractStatus.objects.filter(id=status_id).exists():
            messages.error(request, gettext('Status not found'))
            return redirect('board', board_id=board_id)
        status = ContractStatus.objects.get(pk=status_id)
        if position > status.position:
            ContractStatus.objects.filter(board_id=board_id, position__gt=status.position,
                                          position__lte=position).update(position=F('position') - 1)
        elif position < ContractStatus.objects.get(pk=status_id).position:
            ContractStatus.objects.filter(board_id=board_id, position__gte=position,
                                          position__lt=status.position).update(position=F('position') + 1)

        status.name, status.name_ru, status.name_en, status.color, status.position = name, name, name, color, position
        status.save()
        messages.success(request, gettext("Status changed successfully"))
        return redirect('board', board_id=board_id)


def delete_board(request, board_id):
    if not (Board.objects.filter(pk=board_id).exists()):
        messages.error(request, gettext("Board not found"))
        return redirect('boards')
    board_to_delete = Board.objects.get(pk=board_id)
    if board_to_delete.get_permissions_for_user(request.user).role != BoardPermissions.OWNER:
        messages.error(request, gettext("You do not have permissions to delete this board"))
        return redirect('boards')
    # board_to_delete.contractsset.all().delete()

    board_to_delete.delete()
    return JsonResponse({'status': 'ok'})


def delete_status(request: HttpRequest, board_id: UUID, status_id: UUID):
    if request.method != 'GET':
        messages.add_message(request, messages.ERROR, gettext('Invalid request method'))
        return redirect('boards')

    with transaction.atomic():
        if not Board.objects.filter(id=board_id).exists():
            messages.error(request, gettext('Board not found'))
            return redirect('boards')

        if not ContractStatus.objects.filter(id=status_id).exists():
            messages.error(request, gettext('Status not found'))
            return redirect('board', board_id=board_id)

        status = ContractStatus.objects.get(pk=status_id)
        status.contract_set.update(status=ContractStatus.objects.get(board_id=board_id, name_ru='Удалена'))
        ContractStatus.objects.filter(board_id=board_id, position__gt=status.position).update(
            position=F('position') - 1)
        status.delete()
        messages.success(request, gettext("Status deleted successfully"))

        return redirect('board', board_id=board_id)


def contract(request: HttpRequest, board_id: UUID, contract_id: UUID):
    if not Board.objects.filter(id=board_id).exists():
        messages.error(request, gettext('Board not found'))
        return redirect('boards')

    if not Contract.objects.filter(id=contract_id).exists():
        messages.error(request, gettext('Contract not found'))
        return redirect('board', board_id=board_id)

    selected_contract: Contract = Contract.objects.prefetch_related('board_member', 'contractlog_set').get(
        id=contract_id)
    board: Board = Board.objects.get(pk=board_id)
    board_members = UserModel.objects.filter(
        pk__in=board.get_board_members_permissions().values_list('user_id', flat=True))
    user: UserModel = request.user

    if board.get_permissions_for_user(user).role in [BoardPermissions.OWNER, BoardPermissions.ADMIN]:
        if selected_contract.board_member.company != user.company:
            messages.error(request, gettext('You do not have access to this deal'))
            return redirect('boards')

    elif board.get_permissions_for_user(user).role == BoardPermissions.EMPLOYEE:
        if selected_contract.board_member != user:
            messages.error(request, gettext('You do not have access to this deal'))
            return redirect('boards')

    can_edit_board_member = user.has_perm('change_usermodel')
    logs = selected_contract.contractlog_set.all()
    FormClass = ContractEditForm if can_edit_board_member else ContractEditFormNonOwner

    if request.method == 'GET':
        if not Contract.objects.filter(id=contract_id).exists():
            messages.error(request, gettext('Contract not found'))
            return redirect('boards')

        edit_contract_form = FormClass(instance=selected_contract, board_members=board_members,
                                       user=request.user) if can_edit_board_member else FormClass(
            instance=selected_contract, user=request.user)
        edit_contract_form.fields['contact'].queryset |= UsersContacts.objects.filter(pk=selected_contract.contact.pk)

        ContractLog.create_message(user, 'просмотрел', selected_contract)

        contacts = UsersContacts.objects.filter(
            pk__in=ListContainer.objects.filter(list__list_owner=user).values_list('contact', flat=True))

        file_links = []
        if selected_contract.contractfile_set.exists():
            contract_files = selected_contract.contractfile_set.all()
            media_storage = get_storage_class()()
            for contract_file_object in contract_files:
                file_links.append(media_storage.url(contract_file_object.file))

        return render(request, 'crm/contract.html', context={
            'contract': selected_contract,
            'edit_contract_form': edit_contract_form,
            'logs': logs,
            'contacts': contacts,
            'contract_files': file_links
        })

    if request.method == 'POST':

        # TODO 21.12.22: Авторизация на изменение team_member у контракта
        # TODO 21.12.22: Доделать когда будет поле team_member в модели Contract

        if not Contract.objects.filter(id=contract_id).exists():
            messages.error(request, gettext('Contract not found'))
            return redirect('boards')

        selected_contract: Contract = Contract.objects.get(id=contract_id)

        edit_contract_form = FormClass(request.POST, instance=selected_contract,
                                       board_members=user.company.members.all(),
                                       user=user) if can_edit_board_member else FormClass(
            request.POST, instance=selected_contract, user=user)
        edit_contract_form.fields['contact'].queryset |= UsersContacts.objects.filter(
            pk=selected_contract.contact.pk)

        if edit_contract_form.is_valid():
            edit_contract_form.save()
            files = request.FILES
            new_board_member = edit_contract_form.cleaned_data.get('board_member')

            contract_files: list[InMemoryUploadedFile] = files.getlist(
                'contract_files')

            if contract_files:
                if len(contract_files) + selected_contract.contractfile_set.count() > 10:
                    messages.add_message(
                        request, messages.ERROR, gettext('Too many files'))
                    return redirect('boards')
                if any([file.size > 20 * 1024 * 1024 for file in contract_files]):
                    messages.add_message(request, messages.ERROR, gettext(
                        'File size limit exceeded'))
                    return redirect('boards')

                files_to_create = []
                for file in contract_files:
                    file_path = save_contract_file_in_bucket(
                        file, selected_contract.id)
                    files_to_create.append(ContractFile(
                        file=file_path, contract=selected_contract))

                ContractFile.objects.bulk_create(files_to_create)

            Notification.objects.create(receiver=new_board_member,
                                        text_en=f'{user.email} assigned you to a new contract',
                                        text_ru=f'{user.email} назначил вас к новой сделке',
                                        redirect_url=reverse('contract',
                                                             kwargs={'board_id': board_id, 'contract_id': contract_id}))
            messages.success(request, gettext('Contract successfully updated'))
            ContractLog.create_message(user, 'изменил', selected_contract)
        else:
            messages.error(request, gettext(
                'Contract not updated: ') + str(edit_contract_form.errors))
            ContractLog.create_message(
                user, 'попытался изменить', selected_contract)

        return redirect('contract', board_id=board_id, contract_id=contract_id)


def create_contract(request: HttpRequest, board_id: UUID):
    user: UserModel = request.user

    if request.method != 'POST':
        messages.add_message(request, messages.ERROR, gettext('Invalid request method'))
        return redirect('boards')

    if not Board.objects.filter(id=board_id).exists():
        messages.error(request, gettext('Board not found'))
        return redirect('boards')

    data = request.POST
    files = request.FILES

    name, currency, _sum, description, contact_id = data.get('name'), data.get('currency'), data.get('sum'), data.get(
        'description'), data.get('contact')

    if not (name and currency and _sum and description and contact_id):
        messages.add_message(request, messages.ERROR, gettext('Invalid data'))
        return redirect('boards')

    contact = UsersContacts.objects.get(pk=contact_id)

    created_contract = Contract.objects.create(name=name,
                                               status=ContractStatus.objects.get(board_id=board_id, name_ru='Новая'),
                                               currency_id=currency,
                                               sum=_sum, description=description, contact=contact, board_member=user)
    Board.objects.get(pk=board_id).log_action(user, BoardLog.CONTRACT_CREATED_ACTION,
                                              description=f"Пользователь {user.email} создал контракт {created_contract.name}"
                                                          f" в доске  {Board.objects.get(pk=board_id).name} ({Board.objects.get(pk=board_id).id})")

    contract_files: list[InMemoryUploadedFile] = files.getlist('contract_files')
    if contract_files:
        if len(contract_files) > 10:
            messages.add_message(request, messages.ERROR,
                                 gettext('Too many files'))
            return redirect('boards')
        if any([file.size > 20 * 1024 * 1024 for file in contract_files]):
            messages.add_message(request, messages.ERROR,
                                 gettext('File size limit exceeded'))
            return redirect('boards')

        files_to_create = []
        for file in contract_files:
            file_path = save_contract_file_in_bucket(file, created_contract.id)
            files_to_create.append(ContractFile(
                file=file_path, contract=created_contract))

        ContractFile.objects.bulk_create(files_to_create)

    messages.add_message(request, messages.SUCCESS, gettext('Contract successfully created'))
    return redirect('board', board_id=board_id)


def transfer_contract(request, board_id, contract_id):
    if not Board.objects.filter(id=board_id).exists():
        messages.error(request, gettext('Board not found'))
        return redirect('boards')

    if not Contract.objects.filter(id=contract_id).exists():
        messages.error(request, gettext('Contract not found'))
        return redirect('board', board_id=board_id)

    current_contract = Contract.objects.get(pk=contract_id)

    if current_contract.status.name_ru == 'Сделка успешна' or current_contract.status.name_ru == 'Удалена' or current_contract.status.name_ru == 'Сделка провалена':
        messages.error(request, gettext('Unable to change contract status'))
        return redirect('board', board_id=board_id)

    current_contract.status = ContractStatus.objects.get(pk=request.POST['transfer_contract'])
    current_contract.last_status_changed = timezone.now()
    current_contract.save()
    Board.objects.get(pk=board_id).log_action(request.user, BoardLog.CONTRACT_STATUS_CHANGED_ACTION,
                                              description=f"Статус сделки {current_contract.name}({current_contract.id}) изменен на {current_contract.status.name_ru} пользователем {request.user.email}")
    return redirect('board', board_id=board_id)


def add_contract_to_trash(request, board_id, contract_id):
    if not Board.objects.filter(id=board_id).exists():
        messages.error(request, gettext('Board not found'))
        return redirect('boards')

    if not Contract.objects.filter(id=contract_id).exists():
        messages.error(request, gettext('Contract not found'))
        return redirect('board', board_id=board_id)

    current_contract = Contract.objects.get(pk=contract_id)
    current_contract.status = ContractStatus.objects.get(board_id=board_id, name_ru="Удалена")
    current_contract.save()
    return redirect('board', board_id=board_id)


def delete_contract(request, board_id, contract_id):
    if not Board.objects.filter(id=board_id).exists():
        messages.error(request, gettext('Board not found'))
        return redirect('boards')

    if not Contract.objects.filter(id=contract_id).exists():
        messages.error(request, gettext('Contract not found'))
        return redirect('board', board_id=board_id)

    current_contract = Contract.objects.get(pk=contract_id)
    Board.objects.get(pk=board_id).log_action(request.user, BoardLog.CONTRACT_DELETED_ACTION,
                                              description=f"Пользователь {request.user.email}"
                                                          f" удалил контракт {current_contract.name}({current_contract.id})")

    current_contract.delete()
    return redirect('board', board_id=board_id)


def update_currencies_rate():
    last_check = Currency.objects.get(name="USD").last_check
    if (timezone.now() - last_check) > datetime.timedelta(hours=6):
        curr_list = ["RUB", "USD", "EUR", "AZN", "AMD", "BYN",
                     "KZT", "KGS", "CNY", "MDL", "TJS", "TMT", "UZS", "UAH"]
        today_date = datetime.datetime.now().strftime('%d/%m/%Y')
        url = "http://www.cbr.ru/scripts/XML_daily.asp?date_req=" + today_date
        response = requests.get(url)

        dict_data = xmltodict.parse(response.content)

        usd_currency = list(
            filter(lambda x: x['CharCode'] == "USD", dict_data['ValCurs']['Valute']))[0]

        usd_rate = float((usd_currency['Value']).replace(',', '.'))
        rub = Currency.objects.get(name="RUB")
        rub.value = usd_rate
        rub.last_check = timezone.now()
        rub.save()

        for elem in dict_data['ValCurs']['Valute']:
            if elem["CharCode"] in curr_list:
                value_in_rub = float(elem["Value"].replace(
                    ",", ".")) / int(elem['Nominal'])
                value_in_usd = usd_rate / value_in_rub

                if elem["CharCode"] == "USD":
                    currency = Currency.objects.get(name="USD")
                    currency.last_check = timezone.now()
                    currency.save()
                else:
                    currency = Currency.objects.get(name=elem["CharCode"])
                    currency.value = value_in_usd
                    currency.last_check = timezone.now()
                    currency.save()


def count_in_usd(contracts: QuerySet[Contract]):
    _sum = np.sum([contract.sum / contract.currency.value for contract in contracts])
    return _sum


def get_contracts_data(request: HttpRequest):
    data = request.GET
    user, board, currency, board_member_id = request.user, Board.objects.get(
        pk=data.get('board_id')), Currency.objects.get(pk=data.get('currency_id')), int(data.get("board_member_id"))
    statuses: QuerySet[ContractStatus] = board.contractstatus_set.all()

    data = [
        status.contract_set.filter(
            board_member__company=user.company) if user.current_company_role != UserModel.EMPLOYEE and not board_member_id else status.contract_set.filter(
            board_member_id=board_member_id) if user.current_company_role == UserModel.EMPLOYEE or board_member_id else Contract.objects.none()
        for status in statuses
    ]

    result = [round(float(currency.value) * float(count_in_usd(contracts)), 1) for contracts in data]
    common_sum = max(result)
    _statuses = {status.name: status.hex_color for status in statuses}
    return JsonResponse({"data": result, "statuses": _statuses, "common_sum": common_sum, "currency": currency.name})


def filter_contracts_data(request: HttpRequest):
    data = request.GET
    user, board, currency, board_member_id, hours, period_from, period_to = request.user, Board.objects.get(
        pk=data.get('board_id')), Currency.objects.get(pk=data.get('currency_id')), int(
        data.get("board_member_id")), int(data.get('hours')), data.get('period_from'), data.get('period_to')
    statuses: QuerySet[ContractStatus] = board.contractstatus_set.all()

    if hours:
        data = [
            status.contract_set.filter(board_member__company=user.company, last_status_changed__gte=(
                    timezone.now() - datetime.timedelta(hours=int(
                hours)))) if user.current_company_role != UserModel.EMPLOYEE and not board_member_id else status.contract_set.filter(
                board_member_id=board_member_id, last_status_changed__gte=(timezone.now() - datetime.timedelta(
                    hours=int(
                        hours)))) if user.current_company_role == UserModel.EMPLOYEE or board_member_id else Contract.objects.none()
            for status in statuses
        ]
    else:
        data = [
            status.contract_set.filter(board_member__company=user.company, last_status_changed__gte=period_from,
                                       last_status_changed__lte=period_to) if user.current_company_role != UserModel.EMPLOYEE and not board_member_id else status.contract_set.filter(
                board_member_id=board_member_id, last_status_changed__gte=period_from,
                last_status_changed__lte=period_to) if user.current_company_role == UserModel.EMPLOYEE or board_member_id else Contract.objects.none()
            for status in statuses
        ]

    result = [round(float(currency.value) * float(count_in_usd(contracts)), 1) for contracts in data]

    if not np.sum(result):
        result = 0

    _statuses = {status.name: status.hex_color for status in statuses}
    return JsonResponse({"data": result, "statuses": _statuses})


def update_stats_table(request: HttpRequest):
    board, currency = Board.objects.get(pk=request.GET.get('board_id')), Currency.objects.get(
        pk=request.GET.get('currency_id'))
    statuses, board_members = board.contractstatus_set.all(), [permission.user for permission in
                                                               board.boardpermissions_set.all()]
    board_member_stat = get_member_stats(board_members, statuses, currency)
    return render(request, 'crm/includes/stats_table.html',
                  context={'statuses': statuses, 'board_member_stat': board_member_stat})


def contracts_statistic(request: HttpRequest):
    update_currencies_rate()

    user: UserModel = request.user
    boards = Board.get_user_boards(user)
    first_board, first_currency = boards.first(), Currency.objects.first()

    board_permission, statuses, board_member_stat = None, ContractStatus.objects.none(), None
    if first_board:
        board_permission, statuses, board_members = first_board.get_permissions_for_user(user).role, first_board.contractstatus_set.all(), [permission.user for permission in first_board.boardpermissions_set.all()]
        board_member_stat = get_member_stats(board_members, statuses, first_currency)

    currencies = Currency.objects.all()

    curr_list = ["RUB", "USD", "EUR", "AZN", "AMD", "BYN", "KZT", "KGS", "CNY", "MDL", "TJS", "TMT", "UZS", "UAH"]
    ordered_currencies = [currencies.get(name=curr) for curr in curr_list]

    board_members = UserModel.objects.filter(company=user.company) if board_permission != "EMPL" else [user]
    context = {
        'board_permission': board_permission,
        'boards': boards,
        'statuses': statuses,
        'board_member_stat': board_member_stat,
        'currencies': ordered_currencies,
        'board_members': board_members,
    }
    return render(request, 'crm/contracts_statistic.html', context=context)


def contracts_by_teammember(request: HttpRequest):
    user, team_member_id, statuses = request.user, request.GET.get(
        'team_member_id'), ContractStatus.objects.all()

    if team_member_id:
        data = {status: status.contract_set.filter(
            team_member_id=team_member_id) for status in statuses}
    else:
        data = {status: status.contract_set.filter(team_member__company=user.company) if user.current_company_role in [
            UserModel.OWNER, UserModel.ADMIN] else status.contract_set.filter(
            team_member=request.user) if user.current_company_role == UserModel.EMPLOYEE else Contract.objects.none()
                for status in statuses}

    context = {
        'data': data
    }

    return render(request, 'crm/includes/contracts_list.html', context=context)


def delete_attachment(request: HttpRequest, contract_id):
    if request.method == "POST":
        contract = Contract.objects.get(pk=contract_id)
        attachment_number_to_delete = request.POST.get('attachment_number')
        contract.contractfile_set.all()[int(
            attachment_number_to_delete)].delete()
        return JsonResponse({"status": "ok"})
    return JsonResponse({"status": "error", 'message': 'Method not allowed'}, status=405)


def create_contact_from_contract(request: HttpRequest):
    if request.method != 'POST':
        messages.add_message(request, messages.ERROR,
                             gettext('Invalid request method'))
        return redirect('boards')

    data = request.POST

    if data['site']:
        company_for_contact, created = ContactCompany.objects.get_or_create(company_site__iexact=data['site'],
                                                                            defaults={'company_name': data['company'],
                                                                                      'company_site': data['site']})
    else:
        company_for_contact, created = ContactCompany.objects.get_or_create(company_name__iexact=data['company'],
                                                                            company_site__iexact=data['site'],
                                                                            defaults={'company_name': data['company'],
                                                                                      'company_site': data['site']})

    if company_for_contact.company_name == "":
        company_for_contact.company_name = data['company']

    list, created = List.objects.get_or_create(
        list_name='contacts_from_contract', list_owner=request.user)

    contact: UsersContacts = UsersContacts(name=data.get('first_name'), surname=data.get('surname'),
                                           middle_name=data.get('middle_name'), phone=data.get('phone_number'),
                                           position_in_company=data.get('position'), email=data.get('email'),
                                           company=company_for_contact)

    container: ListContainer = ListContainer(list=list, contact=contact)
    company_for_contact.save()
    contact.save()
    container.save()

    request.user.company.save()

    contact_data = {
        'id': contact.pk,
        'full_name': contact.full_name,
        'email': contact.email,
        'phone': str(contact.phone),
        'company_name': company_for_contact.company_name,
        'company_site': company_for_contact.company_site
    }

    return JsonResponse(contact_data)


def change_contracts_contact(request: HttpRequest):
    if request.method != 'GET':
        messages.add_message(request, messages.ERROR,
                             gettext('Invalid request method'))
        return redirect('boards')

    data = request.GET

    contract_id, contact_id = data.get('contract_id'), data.get('contact_id')
    contract, contact = Contract.objects.get(
        pk=contract_id), UsersContacts.objects.get(pk=contact_id)

    contract.contact, contract.company = contact, contact.company
    contact.save()

    contact_data = {
        'email': contact.email,
        'phone': str(contact.phone),
        'company_name': contact.company.company_name if contact.company else '',
        'company_site': contact.company.company_site if contact.company else ''
    }
    return JsonResponse(contact_data)
