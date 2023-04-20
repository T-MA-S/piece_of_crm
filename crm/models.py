import uuid

from django.db import models
from django.db.models import Q, QuerySet
from django.utils import timezone

from users.models import UserModel
from .choices import ContractStatusColorChoices


class Currency(models.Model):
    name = models.CharField(max_length=5)
    full_name = models.TextField(null=True)
    value = models.DecimalField(max_digits=10, decimal_places=2)
    last_check = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Валюта'
        verbose_name_plural = 'Валюты'


class Board(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Доска'
        verbose_name_plural = 'Доски'

    def get_owner(self) -> UserModel:
        return BoardPermissions.objects.get(board=self, role=BoardPermissions.OWNER).user

    @classmethod
    def get_user_boards(cls, user) -> QuerySet['Board']:
        return cls.objects.filter(boardpermissions__user=user)

    @classmethod
    def get_user_owns_boards(cls, user) -> QuerySet['Board']:
        return cls.objects.filter(boardpermissions__user=user, boardpermissions__role=BoardPermissions.OWNER)

    @classmethod
    def get_user_non_owns_boards(cls, user) -> QuerySet['Board']:
        # FIXME: Пытался делать через exclude, но не получилось
        # FIXME: return cls.objects.filter(boardpermissions__user=user).exclude(boardpermissions__role=BoardPermissions.OWNER)
        # FIXME: Посмотрите, мб у вас получится переписать
        return cls.objects.filter(Q(boardpermissions__role=BoardPermissions.ADMIN, boardpermissions__user=user) |
                                  Q(boardpermissions__role=BoardPermissions.EMPLOYEE, boardpermissions__user=user))

    def get_board_members_permissions(self) -> QuerySet['BoardPermissions']:
        return BoardPermissions.objects.filter(board=self)

    def get_board_invites(self) -> QuerySet['BoardInvite']:
        return BoardInvite.objects.filter(board=self)

    def get_permissions_for_user(self, user: 'UserModel') -> 'BoardPermissions':
        return BoardPermissions.objects.filter(board=self, user=user).first()

    def can_user_invite_members(self, user: 'UserModel') -> bool:
        return self.get_permissions_for_user(user).role in [BoardPermissions.OWNER, BoardPermissions.ADMIN]

    def can_edit_role(self, user: 'UserModel'):
        return self.get_permissions_for_user(user).role == BoardPermissions.OWNER

    def invite_user(self, user: 'UserModel') -> 'BoardInvite':
        if (existing_invite := BoardInvite.objects.filter(board=self, user=user, status=BoardInvite.PENDING)).exists():
            return existing_invite.first()
        invite = BoardInvite.objects.create(board=self, user=user)
        return invite

    def can_manage_board(self, user):
        return self.get_permissions_for_user(user) and self.get_permissions_for_user(user).role in [
            BoardPermissions.OWNER, BoardPermissions.ADMIN]

    def retrieve_board_logs(self, requested_user: 'UserModel') -> QuerySet['BoardLog']:
        match self.get_permissions_for_user(requested_user).role:
            case BoardPermissions.OWNER | BoardPermissions.ADMIN:
                return BoardLog.objects.filter(board=self)
            case BoardPermissions.EMPLOYEE:
                return BoardLog.objects.filter(board=self, user=requested_user)

    def log_action(self, user: 'UserModel', action: str, description: str) -> 'BoardLog':
        return BoardLog.objects.create(board=self, user=user, action=action, description=description)


class BoardPermissions(models.Model):
    
    OWNER = 'OWN'
    ADMIN = 'ADMIN'
    EMPLOYEE = 'EMPL'
    roles = (
        (OWNER, 'Owner'),
        (ADMIN, 'ADMIN'),
        (EMPLOYEE, 'Employee'),
    )

    board = models.ForeignKey(Board, on_delete=models.CASCADE)
    user = models.ForeignKey(UserModel, on_delete=models.CASCADE)
    role = models.CharField(max_length=25, choices=roles)

    def __str__(self):
        return f'{self.user.email} {self.role} доски {self.board.name}'


class BoardInvite(models.Model):
    PENDING = 'PEND'
    ACCEPTED = 'ACPT'
    DENIED = 'DEND'

    statuses = [
        (PENDING, 'Pending'),
        (ACCEPTED, 'Accepted'),
        (DENIED, 'Denied')
    ]

    board = models.ForeignKey(Board, on_delete=models.CASCADE)
    user = models.ForeignKey(UserModel, on_delete=models.CASCADE)
    status = models.CharField(max_length=128, default=PENDING, choices=statuses)

    def accept_invite(self) -> BoardPermissions:
        self.status = self.ACCEPTED
        self.save()
        return BoardPermissions.objects.create(board=self.board, user=self.user, role=BoardPermissions.EMPLOYEE)

    def decline_invite(self):
        self.status = self.DENIED
        self.save()


class BoardLog(models.Model):
    CONTRACT_CREATED_ACTION = 'CONTRACT_CREATED'
    CONTRACT_STATUS_CHANGED_ACTION = 'CONTRACT_STATUS_CHANGED'
    CONTRACT_DELETED_ACTION = 'CONTRACT_DELETED'
    STATUS_ADDED_ACTION = 'STATUS_ADDED'
    STATUS_DELETED_ACTION = 'STATUS_DELETED'

    actions = [
        (CONTRACT_CREATED_ACTION, 'Создан договор'),
        (CONTRACT_STATUS_CHANGED_ACTION, 'Изменен статус договора'),
        (CONTRACT_DELETED_ACTION, 'Удален договор'),
        (STATUS_ADDED_ACTION, 'Добавлен статус'),
        (STATUS_DELETED_ACTION, 'Удален статус'),
    ]

    board = models.ForeignKey(Board, on_delete=models.CASCADE, related_name='logs')
    user = models.ForeignKey(UserModel, on_delete=models.CASCADE)
    action = models.CharField(max_length=255, choices=actions)
    created_at = models.DateTimeField(auto_now_add=True)
    description = models.TextField(null=True)

    def __str__(self):
        return f'{self.user.email} {self.action} доски {self.board.name}'

    class Meta:
        verbose_name = 'Лог доски'
        verbose_name_plural = 'Логи доски'


class ContractStatus(models.Model):

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    board = models.ForeignKey(Board, on_delete=models.CASCADE, null=True)
    name = models.CharField(max_length=255)
    color = models.CharField(max_length=20, choices=ContractStatusColorChoices.choices, default=ContractStatusColorChoices.WHITE)
    position = models.PositiveSmallIntegerField()

    def __str__(self):
        return self.name
    
    @property
    def hex_color(self) -> str:
        colors = {
            'primary': '#0d6efd',
            'secondary': '#6c757d',
            'success': '#198754',
            'danger': '#dc3545',
            'warning': '#ffc107',
            'info': '#0dcaf0',
            'white': '#f8f9fa',
        }
        return colors.get(self.color)

    class Meta:
        ordering = ['position']
        verbose_name = 'Статус'
        verbose_name_plural = 'Статусы'


class Contract(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    name = models.CharField(max_length=255)
    status = models.ForeignKey(ContractStatus, on_delete=models.CASCADE)
    sum = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.ForeignKey(Currency, on_delete=models.PROTECT)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    contact = models.ForeignKey('company.UsersContacts', on_delete=models.PROTECT)
    board_member = models.ForeignKey('users.UserModel', on_delete=models.PROTECT)
    last_status_changed = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Сделка'
        verbose_name_plural = 'Сделки'


class ContractLog(models.Model):
    created_at = models.DateTimeField('Время записи лога', auto_now_add=True)
    contract: Contract = models.ForeignKey(Contract, on_delete=models.CASCADE)
    message = models.TextField('Сообщение')

    @classmethod
    def create_message(cls, user: UserModel, action: str, contract: Contract) -> 'ContractLog':
        message = f'{user.email} {action} сделку {contract.id}'
        log = cls.objects.create(contract=contract, message=message)
        return log


class ContractFile(models.Model):
    contract = models.ForeignKey(Contract, on_delete=models.CASCADE)
    file = models.URLField(max_length=1000)
