from django.http import HttpResponse, HttpRequest
from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils.translation import gettext

from .utils import getlanguage, generate_receipt

from .models import RobokassaTransaction, PromoCode
from .services import *

from SalesTech.settings import ROBOKASSA_MERCHANT_LOGIN, ROBOKASSA_MERCHANT_PASSWORD_1, ROBOKASSA_MERCHANT_PASSWORD_2, ROBOKASSA_ISTEST

from logger.models import Logs


def create_payment(request: HttpRequest, rate_hash):
    return create_transaction(request, rate_hash)


def restart_payment(request: HttpRequest, transaction_hash):
    user = request.user
    if RobokassaTransaction.objects.filter(hash=transaction_hash).exists():

        if canceledtransactions(transaction_hash):
            messages.add_message(request, messages.ERROR, gettext('Transaction canceled'))
            return redirect('transactions')

        merchant_login = ROBOKASSA_MERCHANT_LOGIN  # Идентификатор магазина
        password_1 = ROBOKASSA_MERCHANT_PASSWORD_1  # пароль №1

        transaction: RobokassaTransaction = RobokassaTransaction.objects.get(hash=transaction_hash)

        out_sum = transaction.price  # Сумма
        invid = transaction.pk  # Номер заказа
        description = transaction.description  # описание заказа

        culture = getlanguage(request)  # язык

        receipt = generate_receipt(description, out_sum)

        link = generate_payment_link(merchant_login=merchant_login, merchant_password_1=password_1,
                                     cost=out_sum, invid=invid, receipt=receipt, description=description, culture=culture, user=user, is_test=ROBOKASSA_ISTEST)
        
        Logs.info(f"Рестарт транзакции. ID пользователя: {user.id}. Тарифный план: {transaction.plan.name}. Сумма: {out_sum}. ID транзакции: {invid}", Logs.ROBOKASSA)
        
        return redirect(link)
    else:
        Logs.error(f"Рестарт транзакции. ID пользователя: {user.id}. Ошибка: Тарифный план не найден", Logs.ROBOKASSA)
        messages.add_message(request, messages.ERROR,
                             gettext('Invalid payment details'))
        return redirect('account')


def result_payment(request: HttpRequest):
    password_2 = ROBOKASSA_MERCHANT_PASSWORD_2  # пароль №2
    result = res_payment(password_2, request.build_absolute_uri())
    return HttpResponse(result)


def success_payment(request: HttpRequest):
    password_1 = ROBOKASSA_MERCHANT_PASSWORD_1  # пароль №1
    success, plan_name = check_success_payment(password_1, request.build_absolute_uri())
    if success:
        messages.add_message(request, messages.SUCCESS, gettext(
            'You have successfully purchased a plan: ') + plan_name)
    else:
        messages.add_message(request, messages.ERROR,
                             gettext('Oops... An error has occurred'))
    return redirect('account')


def fail_payment(request: HttpRequest):
    transaction_id = failpayment(request.build_absolute_uri())
    transaction: RobokassaTransaction = RobokassaTransaction.objects.get(pk=transaction_id)
    Logs.info(f"Неудачный платежь. ID пользователя: {transaction.user.pk}. ID транзакции: {transaction.pk}", Logs.ROBOKASSA)
    messages.add_message(request, messages.ERROR,
                         gettext('Oops... An error has occurred'))
    return redirect('account')


def cancel_transaction(request: HttpRequest, transaction_hash):
    result = canceltransaction(transaction_hash)
    if result:
        return redirect('transactions')
    else:
        messages.add_message(request, messages.ERROR,
                             gettext('Invalid payment details'))
        return redirect('transactions')


def user_transactions(request: HttpRequest):
    user = request.user
    transactions = getusertransactions(user)
    return render(request, 'payment/transactions.html', {'transactions': transactions})


def activate_promo_code(request: HttpRequest, rate_hash: str):
    user = request.user
    if request.method == 'POST':
        promo_code = request.POST.get('promo_code', None)
        if promo_code:
            if PromoCode.objects.filter(promo_code=promo_code, count__gt=0, date_from__lte=timezone.now(), date_to__gte=timezone.now()).exists():
                promo: PromoCode = PromoCode.objects.get(promo_code=promo_code)
                if not user.promo_codes.filter(pk=promo.pk).exists():
                    return create_transaction(request, rate_hash, promo)
                else:
                    Logs.error(f"Новая транзакция. ID пользователя: {user.id}. Ошибка: Промокод уже активирован", Logs.ROBOKASSA)
                    messages.add_message(request, messages.ERROR, gettext('Promo code already activated'))
                    return redirect('account')
        
        Logs.error(f"Новая транзакция. ID пользователя: {user.id}. Ошибка: Промо код не найден", Logs.ROBOKASSA)
        messages.add_message(request, messages.ERROR, gettext('Promo code not found'))
        return redirect('account')

    Logs.error(f"Новая транзакция. ID пользователя: {user.id}. Ошибка: Тарифный план не найден", Logs.ROBOKASSA)
    messages.add_message(request, messages.ERROR, gettext('Invalid payment details'))
    return redirect('account')
