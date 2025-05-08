
from django.contrib import admin
from django.urls import path
from django.shortcuts import redirect
from apartment_management.views import nguoi_dung_views, nhan_khau_views, thu_phi_views

urlpatterns = [
    path('login/', nguoi_dung_views.login_view, name='login'),
    path('', lambda request: redirect('login')),
    # path('users/', nguoi_dung_views.list_users, name='list_users'),
]
