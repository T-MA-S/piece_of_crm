import decimal
import hashlib
from urllib.parse import urlparse, urlencode

from django.utils.translation import get_language_from_request

from logger.models import Logs



def transaction_hash(rate_id):
    return hashlib.sha256(f'sales-trans-action-{rate_id}-tech'.encode('utf-8')).hexdigest()


def generate_signature(*args) -> str:
    return hashlib.sha512(':'.join(str(arg) for arg in args).encode()).hexdigest()


def parse_response(request: str) -> dict:

    params = {}

    for item in urlparse(request).query.split('&'):
        key, value = item.split('=')
        params[key] = value
    return params


def check_signature_result(order_number: int, received_sum: decimal, received_signature: hex, password: str) -> bool:
    signature = generate_signature(received_sum, order_number, password)
    if signature.lower() == received_signature.lower():
        return True
    return False


def generate_receipt(description: str, price: int) -> dict:
    receipt =  urlencode({
        "sno": "usn_income",
        "items": [
              {
                  "name": description,
                  "quantity": 1,
                  "sum": price,
                  "payment_method": "full_payment",
                  "payment_object": "service",
                  "tax": "none"
              }
        ]
    })
    return receipt


def get_transaction_status(transaction):
    if transaction.payed_time:
        return 'success'
    elif transaction.canceled_time:
        return 'danger'
    else:
        return ''


def getlanguage(request):
    return get_language_from_request(request)


def promo_code(price_rubles: float, promo):
    return float(price_rubles - (price_rubles * float(promo.discount) / 100))
