from django.urls import path

from .views import *

urlpatterns = [
    path('create/<str:rate_hash>/', create_payment, name='create_payment'),
    path('restart/<str:transaction_hash>/', restart_payment, name='restart_payment'),
    path('cancel/<str:transaction_hash>/', cancel_transaction, name='cancel_transaction'),
    path('result/', result_payment),
    path('success/', success_payment),
    path('fail/', fail_payment),

    path('promo/activate/<str:rate_hash>/', activate_promo_code, name='activate_promo_code')
]