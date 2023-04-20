def start_sending_mails():
    from .scheduler import send_emails, send_telegram_mails
    send_emails()
    send_telegram_mails()


def start_email_checker():
    from .checker import checker, emails
    checker(emails)


def start_rateplan_checker():
    from users.utils import check_plan_period
    check_plan_period()
