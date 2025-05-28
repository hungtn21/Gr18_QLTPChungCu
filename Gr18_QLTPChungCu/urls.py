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
    #==========================Admin routes=========================================================
    path('admin/user-management/', nguoi_dung_views.user_management, name='admin_user_management'),
    path('admin/user-management/create-new-user', nguoi_dung_views.create_new_user, name='create_new_user'),
    path('admin/change-password/', nguoi_dung_views.change_password, name='admin_change_password'),
    path('admin/edit-profile/', nguoi_dung_views.edit_profile, name='admin_edit_profile'),
    path('logout/', nguoi_dung_views.logout_view, name='admin_logout'),
    # path('users/', nguoi_dung_views.list_users, name='list_users'),
    # path('dashboard/admin/', nguoi_dung_views.admin_dashboard, name='AdminDashboard'),
    path('dashboard/bqlcc/', nguoi_dung_views.bqlcc_dashboard, name='BQLCCDashboard'),
    path('dashboard/ketoan/', nguoi_dung_views.kt_dashboard, name='KTDashboard'),
    path('admin/user-management/toggle-status/<int:user_id>/', nguoi_dung_views.toggle_user_status, name='toggle_user_status'),
    #==========================Ke toan routes=========================================================
    path('ketoan/view-list-khoanthu', thu_phi_views.view_list_khoanthu, name='view_list_khoanthu'),
    path('ketoan/create-khoanthu', thu_phi_views.create_khoanthu, name='create_khoanthu'),
    path('ketoan/update-khoanthu/<int:pk>', thu_phi_views.update_khoanthu, name='update_khoanthu' ),
    path('ketoan/delete-khoanthu/<int:pk>', thu_phi_views.delete_khoanthu, name='delete_khoanthu'),

    
    #========================== QLCC routes=========================================================
    
    path('thongke_do_tuoi/', nhan_khau_views.thongKeDoTuoi, name='thongKeDoTuoi'),
    path('thongke_tam_tru/', nhan_khau_views.thongKeTamTru, name='thongKeTamTru'),
    path('thongke_bien_dong/', nhan_khau_views.thongKeBienDong, name='thongKeBienDong'),
    path('lichsu_thaydoi/', nhan_khau_views.lichSuThayDoi, name='lichSuThayDoi'),
    path('bqlcc/change-password/', nhan_khau_views.change_password, name='nhan_khau_change_password'),
    path('bqlcc/edit-profile/', nhan_khau_views.edit_profile, name='nhan_khau_edit_profile'),

]