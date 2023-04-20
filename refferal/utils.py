import hashlib
import string
import random

from django.urls import reverse

from refferal.models import InviteModel
from users.models import CompanyModel


def random_string(string_length=10) -> str:
    letters = string.ascii_lowercase
    some_str = ''.join(random.choice(letters) for i in range(string_length))
    hash_object = hashlib.sha256(str.encode(some_str))
    hex_dig = hash_object.hexdigest()

    return hex_dig


def generate_invite(company: CompanyModel) -> InviteModel:
    the_string = random_string()
    invite = InviteModel.objects.create(url=the_string, company_id=company.id)
    return invite


def create_invite_code(company: CompanyModel) -> str:
    invite = generate_invite(company)
    return invite.url


def get_invite_link(company: CompanyModel, request):
    invite_code = create_invite_code(company)
    invite_link = reverse('ref_link', kwargs={"access_code": invite_code})
    return request.build_absolute_uri(invite_link)
