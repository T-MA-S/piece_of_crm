from django.utils import timezone
from django.http import HttpResponse, HttpRequest
from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils.translation import gettext, gettext_lazy
from django.db import transaction as db_transaction

from datetime import timedelta
from urllib.parse import urlencode

from users.models import UserModel

from .utils import *
from .models import RobokassaTransaction, PromoCode
from users.utils import change_rate_plan
from users.models import RatePlan, UserModel

from logger.models import Logs

from SalesTech.settings import ROBOKASSA_MERCHANT_LOGIN, ROBOKASSA_MERCHANT_PASSWORD_1, ROBOKASSA_ISTEST


# Формирование URL переадресации пользователя на оплату.
def generate_payment_link(merchant_login: str, merchant_password_1: str, cost, invid: int, receipt: str, description: str, culture: str, user, is_test: int, promo=None, robokassa_payment_url='https://auth.robokassa.ru/Merchant/Index.aspx') -> str:
    if promo:
        signature = generate_signature(merchant_login, cost, invid, receipt, merchant_password_1, f'Shp_promo={promo.promo_code}')
        data = {
            'MerchantLogin': merchant_login,
            'OutSum': cost,
            'InvId': invid,
            'Receipt': receipt,
            'Shp_promo': promo.promo_code,
            'Description': description,
            'Culture': culture,
            'SignatureValue': signature,
            'IsTest': is_test,
        }
    else:
        signature = generate_signature(merchant_login, cost, invid, receipt, merchant_password_1)
        data = {
            'MerchantLogin': merchant_login,
            'OutSum': cost,
            'InvId': invid,
            'Receipt': receipt,
            'Description': description,
            'Culture': culture,
            'SignatureValue': signature,
            'IsTest': is_test,
        }

    return f'{robokassa_payment_url}?{urlencode(data)}'


# Получение уведомления об исполнении операции (ResultURL).
def res_payment(merchant_password_2: str, request_url: str) -> str:
    param_request = parse_response(request_url)
    
    cost = param_request['OutSum']
    number = param_request['InvId']
    signature = param_request['SignatureValue']

    promo_code = param_request.get('Shp_promo')

    with db_transaction.atomic():
        user_id = RobokassaTransaction.objects.get(pk=number).user.id
        if check_signature_result(number, cost, signature, merchant_password_2) and (transaction := RobokassaTransaction.objects.filter(pk=number, payed_time__isnull=True)).exists():
            if not promo_code or PromoCode.objects.filter(promo_code=promo_code).exists():
                transaction.update(payed_time=timezone.now())
                return f'OK{param_request["InvId"]}'
                
        RobokassaTransaction.objects.filter(pk=number).update(canceled_time=timezone.now())
        Logs.error(f"Получено уведомления об исполнении операции (Ошибка). ID пользователя: {user_id}", Logs.ROBOKASSA)
        return "bad sign"


# Проверка параметров в скрипте завершения операции (SuccessURL).
def check_success_payment(merchant_password_1: str, request_urk: str) -> str:
    param_request = parse_response(request_urk)

    cost = param_request['OutSum']
    number = param_request['InvId']
    signature = param_request['SignatureValue']

    user_id = RobokassaTransaction.objects.get(pk=number).user.id
    if check_signature_result(number, cost, signature, merchant_password_1) and (transactions := RobokassaTransaction.objects.filter(pk=number, payed_time__isnull=False)).exists():
        transaction: RobokassaTransaction = transactions.first()
        change_rate_plan(transaction.user.pk, transaction.plan.pk)
        Logs.info(f"План успешно изменен. ID пользователя: {user_id}", Logs.ROBOKASSA)
        return True, transaction.plan.name
    Logs.error(f"План не изменен (Ошибка). ID пользователя: {user_id}", Logs.ROBOKASSA)
    return False, None


def failpayment(request_url: str) -> str:
    param_request = parse_response(request_url)
    number = param_request.get('InvId')
    return number


def canceltransaction(transaction_hash: str) -> bool:
    if RobokassaTransaction.objects.filter(hash=transaction_hash).exists():
        transaction: RobokassaTransaction = RobokassaTransaction.objects.get(hash=transaction_hash)
        transaction.canceled_time = timezone.now()
        transaction.save()
        Logs.info(f"Транзакция отменена. ID пользователя: {transaction.user.id}. ID транзакции: {transaction.pk}", Logs.ROBOKASSA)
        return True
    else:
        Logs.error(f"Отмена транзакции. ID пользователя: {transaction.user.id}", Logs.ROBOKASSA)
        return False


def getusertransactions(user: UserModel) -> list[dict]:
    return [{'transaction': transaction, 'status': get_transaction_status(transaction)} for transaction in list(RobokassaTransaction.objects.filter(user=user).order_by('-pk'))]


def canceledtransactions(transaction_hash: str):
    if RobokassaTransaction.objects.filter(hash=transaction_hash, created_time__lt=(timezone.now()-timedelta(days=1))).exists():
        RobokassaTransaction.objects.filter(hash=transaction_hash, created_time__lt=(timezone.now()-timedelta(days=1))).update(canceled_time=timezone.now())
        return True
    return False


def create_transaction(request, rate_hash, promo=None):
    user = request.user
    if rate_hash:
        with db_transaction.atomic():
            if RatePlan.objects.filter(hash=rate_hash).exists():

                if RobokassaTransaction.objects.filter(user=request.user, payed_time__isnull=True, canceled_time__isnull=True).exists():
                    _transaction = RobokassaTransaction.objects.get(user=request.user, payed_time__isnull=True, canceled_time__isnull=True)
                    if not canceledtransactions(_transaction.hash):
                        Logs.error(f"Новая транзакция. ID пользователя: {user.id}. Ошибка: Имеется неоплаченная транзакция", Logs.ROBOKASSA)
                        messages.add_message(request, messages.ERROR, gettext('You have an unpaid transaction'))
                        return redirect('transactions')

                rate_plan: RatePlan = RatePlan.objects.get(hash=rate_hash)

                merchant_login = ROBOKASSA_MERCHANT_LOGIN  # Идентификатор магазина
                password_1 = ROBOKASSA_MERCHANT_PASSWORD_1  # пароль №1

                out_sum = rate_plan.price_rubles  # Сумма
                # # out_sum_currency = '' # Валюта счёта

                if promo:
                    out_sum = promo_code(out_sum, promo)
                    promo.count -= 1
                    promo.save()

                    user.promo_codes.add(promo)
                    user.save()
                
                if out_sum == 0:
                    change_rate_plan(user.pk, rate_plan.pk)
                    messages.add_message(request, messages.SUCCESS, gettext('You have successfully purchased a plan: ') + rate_plan.name)
                    return redirect('account')

                description = f'Salestech {rate_plan.name} plan'  # описание заказа
                culture = getlanguage(request)  # язык

                transaction: RobokassaTransaction = RobokassaTransaction.objects.create(
                    user=user, plan=rate_plan, price=out_sum, description=description)

                invid = transaction.pk  # Номер заказа

                receipt = generate_receipt(description, out_sum)
                link = generate_payment_link(merchant_login=merchant_login, merchant_password_1=password_1,
                                            cost=out_sum, invid=invid, receipt=receipt, description=description, culture=culture, user=user, promo=promo, is_test=ROBOKASSA_ISTEST)
                
                Logs.info(f"Новая транзакция. ID пользователя: {user.id}. Тарифный план: {rate_plan.name}. Сумма: {out_sum}. ID транзакции: {invid}", Logs.ROBOKASSA)

                return redirect(link)

    Logs.error(f"Новая транзакция. ID пользователя: {user.id}. Ошибка: Тарифный план не найден", Logs.ROBOKASSA)
    messages.add_message(request, messages.ERROR, gettext('Invalid payment details'))
    return redirect('account')