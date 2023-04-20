from django.shortcuts import HttpResponse, redirect
from django.urls import reverse

from .models import InviteModel
from users.models import CompanyModel, UserModel
import string, random
import hashlib

from .utils import get_invite_link


def generate_link(request):
    company = CompanyModel.objects.get(owner=request.user.id)
    invite_link = get_invite_link(company)

    return HttpResponse(
        f'<a href={invite_link}>{invite_link}</a>'
    )


def ref_link(request, access_code):
    if InviteModel.objects.filter(url=access_code).exists():

        if request.user.is_authenticated:
            current_user = UserModel.objects.get(email=request.user.email)
            current_user.company = InviteModel.objects.get(url=access_code).company
            current_user.save()
            return redirect('my_team')

        else:
            return redirect(reverse('register', kwargs={"refferal_code": access_code}))

        # необходимо ли удалять ссылку сразу после перехода по ней или она многоразовая?
        # InviteModel.objects.filter(url=access_code).delete()

    else:
        return HttpResponse("Bad or expired link.")
