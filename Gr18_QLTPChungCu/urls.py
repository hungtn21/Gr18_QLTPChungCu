"""
URL configuration for Gr18_QLTPChungCu project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.shortcuts import redirect
from apartment_management.views import nguoi_dung_views, nhan_khau_views, thu_phi_views

urlpatterns = [
    path('login/', nguoi_dung_views.login_view, name='login'),
    path('', lambda request: redirect('login')),
    path('admin/user-management/', nguoi_dung_views.login_view, name='admin-user-management'),
    # path('users/', nguoi_dung_views.list_users, name='list_users'),
    path('dashboard/admin/', nguoi_dung_views.admin_dashboard, name='AdminDashboard'),
    path('dashboard/bqlcc/', nguoi_dung_views.bqlcc_dashboard, name='BQLCCDashboard'),
    path('dashboard/ketoan/', nguoi_dung_views.kt_dashboard, name='KTDashboard'),


    #==========================Ke toan routes=========================================================
    path('ketoan/view-list-khoanthu', thu_phi_views.view_list_khoanthu, name='view_list_khoanthu'),
    path('ketoan/create-khoanthu', thu_phi_views.create_khoanthu, name='create_khoanthu'),
    path('ketoan/update-khoanthu/<int:pk>', thu_phi_views.update_khoanthu, name='update_khoanthu' ),
    path('ketoan/delete-khoanthu/<int:pk>', thu_phi_views.delete_khoanthu, name='delete_khoanthu'),

    path('ketoan/view-list-khoannop', thu_phi_views.view_list_khoannop, name='view_list_khoannop'),
    path('ketoan/khoannop-details/<int:pk>', thu_phi_views.khoannop_details, name='khoannop_details'),


    #------------------------BQL CC----------------------
    path('bqlChungCu/quan_ly_nhan_khau', nhan_khau_views.quan_ly_nhan_khau, name='quan_ly_nhan_khau'),
    path('bqlChungCu/quan_ly_ho_khau', nhan_khau_views.quan_ly_ho_khau, name='quan_ly_ho_khau'),
    path('ho_khau/create/', nhan_khau_views.create_ho_khau, name='create_ho_khau'),

]
