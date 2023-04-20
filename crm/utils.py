import datetime
import os
import numpy as np
from uuid import UUID

import requests
import xmltodict
from django.core.files.storage import get_storage_class

from SalesTech.settings import CONTRACTS_FILE_DIRECTORY_IN_BUCKET


def set_statuses(board_id: UUID, board_type: str):
    from .models import ContractStatus
    from .choices import ContractStatusColorChoices

    statuses = [
        ContractStatus(board_id=board_id, name_ru='Новая', name_en='New', color=ContractStatusColorChoices.INFO, position=1)
    ]
    if board_type == 'full':
        statuses.extend([
            ContractStatus(board_id=board_id, name_ru='Подготовка документов', name_en='Preparation of documents', position=2),
            ContractStatus(board_id=board_id, name_ru='Счёт на предоплату', name_en='Prepaid invoice', position=3),
            ContractStatus(board_id=board_id, name_ru='В работe', name_en='In progress', color=ContractStatusColorChoices.WARNING, position=4),
            ContractStatus(board_id=board_id, name_ru='Финальный счёт', name_en='Final score', color=ContractStatusColorChoices.PRIMARY, position=5),
            ContractStatus(board_id=board_id, name_ru='Сделка провалена', name_en='Contract failed', color=ContractStatusColorChoices.DANGER, position=6),
            ContractStatus(board_id=board_id, name_ru='Анализ причины провала', name_en='Analysis of the cause of failure', color=ContractStatusColorChoices.SECONDARY, position=7),
            ContractStatus(board_id=board_id, name_ru='Сделка успешна', name_en='Contract successful', color=ContractStatusColorChoices.SUCCESS, position=8),
            ContractStatus(board_id=board_id, name_ru='Удалена', name_en='Удалена', position=9)
        ])
    elif board_type == 'standart':
        statuses.extend([
            ContractStatus(board_id=board_id, name_ru='Подготовка документов', name_en='Preparation of documents', position=2),
            ContractStatus(board_id=board_id, name_ru='Счёт на предоплату', name_en='Prepaid invoice', position=3),
            ContractStatus(board_id=board_id, name_ru='В работe', name_en='In progress', color=ContractStatusColorChoices.WARNING, position=4),
            ContractStatus(board_id=board_id, name_ru='Сделка успешна', name_en='Contract successful', color=ContractStatusColorChoices.SUCCESS, position=5),
            ContractStatus(board_id=board_id, name_ru='Удалена', name_en='Удалена', position=6)
        ])
    elif board_type == 'abbreviated':
        statuses.extend([
            ContractStatus(board_id=board_id, name_ru='В работe', name_en='In progress', position=2),
            ContractStatus(board_id=board_id, name_ru='Сделка успешна', name_en='Contract successful', color=ContractStatusColorChoices.SUCCESS, position=3),
            ContractStatus(board_id=board_id, name_ru='Удалена', name_en='Удалена', position=4)
        ])
    else:
        statuses.extend([
            ContractStatus(board_id=board_id, name_ru='Удалена', name_en='Removed', position=2)
        ])
    ContractStatus.objects.bulk_create(statuses)


def init_currencies():
    from .models import Currency

    curr_list = ["RUB", "USD", "EUR", "AZN", "AMD", "BYN", "KZT", "KGS", "CNY", "MDL", "TJS", "TMT", "UZS", "UAH"]
    today_date = datetime.datetime.now().strftime('%d/%m/%Y')
    url = "http://www.cbr.ru/scripts/XML_daily.asp?date_req=" + today_date

    response = requests.get(url)

    dict_data = xmltodict.parse(response.content)

    usd_currency = list(filter(lambda x: x['CharCode'] == "USD", dict_data['ValCurs']['Valute']))[0]

    usd_rate = float((usd_currency['Value']).replace(',', '.'))
    if not Currency.objects.filter(name='RUB').exists():
        Currency.objects.create(name="RUB", full_name="Российский рубль", value=usd_rate)
    for elem in dict_data['ValCurs']['Valute']:
        if elem["CharCode"] in curr_list:
            value_in_rub = float(elem["Value"].replace(",", ".")) / int(elem['Nominal'])
            value_in_usd = usd_rate / value_in_rub
            if not Currency.objects.filter(name=elem["CharCode"]).exists():
                if elem["CharCode"] == "USD":
                    Currency.objects.create(name="USD", full_name="Доллар США", value=1)
                else:
                    Currency.objects.create(name=elem["CharCode"], full_name=elem["Name"], value=value_in_usd)


def save_contract_file_in_bucket(file: 'InMemoryUploadedFile', contract_id: int):
    file_directory_within_bucket = f'{CONTRACTS_FILE_DIRECTORY_IN_BUCKET}{contract_id}/{file.name}'
    file_path_within_bukcet = os.path.join(file_directory_within_bucket, file.name).replace('\\', '/')
    media_storage = get_storage_class()()
    media_storage.save(file_path_within_bukcet, file)
    return file_path_within_bukcet


def get_member_stats(board_members, statuses, currency):
    from .views import count_in_usd

    board_member_stat = {}
    for board_member in board_members:
        contracts_sum, contracts_count = 0, []
        for status in statuses:
            contracts = board_member.contract_set.filter(status=status)
            contracts_count.append(contracts.count())
            contracts_sum += round(float(currency.value) * float(count_in_usd(contracts)), 2)

        contracts_count.extend([np.sum(contracts_count), f'{contracts_sum:,} {currency.name}'])
        board_member_stat.update({board_member.email: contracts_count})
    return board_member_stat
