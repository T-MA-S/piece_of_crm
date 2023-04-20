from django.db import models
from django.utils import timezone
from users.models import CompanyModel
import string, random
import hashlib


def randomString(stringLength=10):
    letters = string.ascii_lowercase
    some_str = ''.join(random.choice(letters) for i in range(stringLength))
    hash_object = hashlib.sha256(str.encode(some_str))
    hex_dig = hash_object.hexdigest()

    return hex_dig



class InviteManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(
            expired_date__gte=timezone.now() - timezone.timedelta(hours=24)
        )


class InviteModel(models.Model):
    url = models.CharField(max_length=128, null=True)
    expired_date = models.DateTimeField(auto_now_add=True)
    company = models.ForeignKey(CompanyModel, on_delete=models.CASCADE, null=True)

    objects = InviteManager()

    class Meta:
        verbose_name = "Приглашение"
        verbose_name_plural = "Приглашения"

    def __str__(self):
        return f'{self.url}'
