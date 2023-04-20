from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path('generate_link', views.generate_link, name='generate_link'),
    path('ref_link/<str:access_code>', views.ref_link, name='ref_link'),
]

