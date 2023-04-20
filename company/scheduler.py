import json
import threading
import requests
from .models import *
from dashboard.models import EmailSettings, UserSettings, TelegramBot
from django.core.mail import EmailMultiAlternatives
from django.utils.html import strip_tags, format_html
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.urls import reverse

from django.db import connection

from requests_futures.sessions import FuturesSession
from SalesTech.settings import MILLIONVERIFIER_API_KEY, VERIFIER_URL
from django.core.mail import get_connection, send_mail
import datetime
import pytracking
from pytracking.html import adapt_html


def mail_credit_count_limited(user_id):
    user = UserModel.objects.get(pk=user_id)
    current_company = user.company
    return current_company.mail_credit_count <= 0


def mail_credit_count_down(user_id):
    user = UserModel.objects.get(pk=user_id)
    current_company = user.company
    current_company.mail_credit_count -= 1
    current_company.save()


def is_real_email(email):
    with FuturesSession() as session:
        email_json_list = json.dumps([email])
        value = session.post(
            f'{VERIFIER_URL}/validate_emails/', data=email_json_list)
        result = value.result().json()
        return result['results'][email]


def get_smtp_settings(email):
    owner = email.sendingmails_list.owner
    current_settings_list = UserSettings.objects.get(user=owner)
    current_settings = EmailSettings.objects.get(user_settings_list=current_settings_list, is_using=True)
    return current_settings, owner


def send_emails(sendingmail_list_id=None):
    emails_to_send = SendingMails.objects.filter(active=True, date__lte=timezone.now(),
                                                 sendingmails_list_id=sendingmail_list_id) if sendingmail_list_id else SendingMails.objects.filter(
        active=True, date__lte=timezone.now())

    if not emails_to_send.exists():
        return

    for email in emails_to_send:
        email.active = False
        email.save()
        
    previous_user = None
    for email in emails_to_send:
        try:
            if not is_real_email(email.recipient.email):
                raise Exception("Invalid email")

            smtp_settings, owner = get_smtp_settings(email)
            if previous_user != owner:
                connection = get_connection(host=smtp_settings.smtp_host,
                                            port=smtp_settings.smtp_port,
                                            username=smtp_settings.smtp_username,
                                            password=smtp_settings.smtp_password,
                                            use_tls=(True if smtp_settings.smtp_connection_type == "TLS" else False),
                                            use_ssl=(True if smtp_settings.smtp_connection_type == "SSL" else False))
            send = True
            if not mail_credit_count_limited(owner.id):
                html_email_text = email.message
                if smtp_settings.signature:
                    signature = smtp_settings.signature.replace('\n', '<br>')
                    html_email_text += f'<br> {signature}'

                html_email_text += " " + f"<img src='{email.link}'>"

                conditions = json.loads(email.conditions)  # список списков с условиями для проверки перед отправкой
                if conditions != None:
                    for condition in conditions:
                        if condition[0] == "EMAIL_OPENED":
                            if not SendingMails.objects.filter(pk=condition[1]).exists():
                                send = False
                            else:
                                email_to_check = SendingMails.objects.get(pk=condition[1])
                                if email_to_check.opened_at == None:
                                    send = False

                        if condition[0] == "NOT_EMAIL_OPENED":
                            if not SendingMails.objects.filter(pk=condition[1]).exists():
                                send = False
                            else:
                                email_to_check = SendingMails.objects.get(pk=condition[1])
                                if email_to_check.opened_at != None:
                                    send = False
                if send:
                    text = strip_tags(html_email_text)

                    msg = EmailMultiAlternatives(email.theme, text, smtp_settings.from_email,
                                                 [email.recipient.email],
                                                 connection=connection)
                    msg.attach_alternative(html_email_text, "text/html")
                    email.date = timezone.now()
                    msg.send()
                    previous_user = owner
                    email.status = "Delivered"
                    email.active = False
                    mail_credit_count_down(owner.id)
                else:
                    email.delete()
            else:
                email.status = "Error You have no mail credits"
            if send:
                email.save()

        except Exception as e:
            email.status = "Error"
            email.error_description = str(e)
            email.save()


def get_telegram_settings(email):
    owner = email.sendingmails_list.owner
    bot = bots.first() if (bots := TelegramBot.objects.filter(user=owner, is_using=True)).exists() else None
    return bot, owner


def send_telegram_mail(bot, sending_mail: SendingTelegram):
    data = {
        "chat_id" : sending_mail.recipient.telegram_id,
        "text" : f"<b>{sending_mail.theme}</b>\n\n{sending_mail.message}",
        "parse_mode" : "html"
    }
    response = requests.get(f'https://api.telegram.org/bot{bot.bot_token}/sendMessage', params=data).json()
    return response.get('ok'), response.get('description')


def send_telegram_mails(sendingmail_list_id=None):
    emails_to_send = SendingTelegram.objects.filter(active=True, date__lte=timezone.now(), sendingmails_list_id=sendingmail_list_id).order_by('id') if sendingmail_list_id else SendingTelegram.objects.filter(active=True, date__lte=timezone.now()).order_by('id')

    if not emails_to_send.exists():
        return

    for email in emails_to_send:
            
        try:
            email.active = False

            bot, owner = get_telegram_settings(email)

            if not bot:
                email.status = "Error Telegram bot not found"
                email.save()
                continue

            if mail_credit_count_limited(owner.id):
                email.status = "Error You have no mail credits"
                email.save()
                continue

            if not email.recipient.telegram_id:
                email.status = "Error The contact does not have a telegram id"
                email.save()
                continue

            send, description = send_telegram_mail(bot, email)

            if not send:
                email.status = 'Error'
                email.error_description = str(description)
                email.save()
                continue

            mail_credit_count_down(owner.id)
            email.date = timezone.now()
            email.status = 'Delivered'
            email.save()

        except Exception as e:
            print(e)
            email.status = "Error"
            email.save()
