from django import template

from crm.models import BoardPermissions, Board

register = template.Library()


@register.simple_tag
def can_edit_contract(user, contract):
    return user.is_authenticated and user.can_edit_contract(contract)


@register.simple_tag
def can_remove_board_member(user_permission: 'BoardPermissions', another_user_permission: 'BoardPermissions'):
    if another_user_permission.role == BoardPermissions.OWNER: return False

    match user_permission.role:
        case BoardPermissions.EMPLOYEE:
            return False
        case BoardPermissions.ADMIN:
            return another_user_permission.role == BoardPermissions.EMPLOYEE
        case BoardPermissions.OWNER:
            return True
        case _:
            return False


@register.simple_tag
def can_user_edit_board(user: 'UserModel', board: Board):
    return board.can_manage_board(user)
