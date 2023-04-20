from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator

from users.models import RatePlan, UserModel
from .utils import transaction_hash


class RobokassaTransaction(models.Model):

    plan = models.ForeignKey(RatePlan, verbose_name='План', on_delete=models.SET_NULL, null=True)
    user = models.ForeignKey(UserModel, verbose_name='Пользователь', on_delete=models.SET_NULL, null=True)
    
    price = models.PositiveIntegerField('Цена')
    description = models.CharField('Описание', max_length=256)
    created_time = models.DateTimeField('Время создания', default=timezone.now)
    payed_time = models.DateTimeField('Время оплаты', default=None, null=True)
    canceled_time = models.DateTimeField('Время отмены', default=None, null=True)

    hash = models.CharField(max_length=128, null=True)

    def __str__(self):
        return f'Транзакция {self.pk}'
    
    def save(self, *args, **kwargs):
        super(RobokassaTransaction, self).save(*args, **kwargs)
        if not self.hash:
            self.hash = transaction_hash(self.pk)
            super(RobokassaTransaction, self).save()
    
    class Meta:
        verbose_name = 'Транзакция'
        verbose_name_plural = 'Транзакции'


class PromoCode(models.Model):

    promo_code = models.CharField('Промо код', max_length=20, unique=True)
    discount = models.DecimalField('Скидка', max_digits=4, decimal_places=1, validators=[MinValueValidator(0), MaxValueValidator(100)])
    count = models.PositiveIntegerField('Количество')

    date_from = models.DateTimeField('Начало действия', blank=True, null=True)
    date_to = models.DateTimeField('Конец действия', blank=True, null=True)

    def __str__(self):
        return f'Промо код {self.pk}'

    class Meta:
        verbose_name = 'Промо код'
        verbose_name_plural = 'Промо коды'


