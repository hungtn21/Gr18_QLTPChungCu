from django.contrib import admin
from django.urls import path
from django.shortcuts import redirect
from apartment_management.views import nguoi_dung_views, nhan_khau_views, thu_phi_views

urlpatterns = [
    path("admin/", admin.site.urls),
    path('login/', nguoi_dung_views.login_view, name='login'),
    path('', lambda request: redirect('login')),
    path('admin/user-management/', nguoi_dung_views.login_view, name='admin-user-management'),
    # path('users/', nguoi_dung_views.list_users, name='list_users'),
    path('dashboard/admin/', nguoi_dung_views.admin_dashboard, name='AdminDashboard'),
    path('dashboard/bqlcc/', nguoi_dung_views.bqlcc_dashboard, name='BQLCCDashboard'),
    path('dashboard/ketoan/', nguoi_dung_views.kt_dashboard, name='KTDashboard'),
    #==========================Ke toan routes=========================================================
    path('ketoan/view-list-dot-thu/', thu_phi_views.list_dot_thu_view, name='list_dot_thu'),
    path('ketoan/dot-thu-details/<int:dot_id>/', thu_phi_views.chi_tiet_dot_thu_view, name='detail_dot_thu'),
    path('ketoan/dot-thu/edit/<int:dot_id>/', thu_phi_views.sua_dot_thu_view, name='edit_dot_thu'),
    path('api/khoan-thu/', thu_phi_views.api_khoan_thu_list, name='api_khoan_thu_list'), 
    path('ketoan/dot-thu/delete/<int:dot_id>/', thu_phi_views.xoa_dot_thu_view, name='xoa_dot_thu'),
    path('ketoan/dot-thu/create/', thu_phi_views.tao_dot_thu_view, name='tao_dot_thu_view'),
    path('ketoan/edit-profile/', thu_phi_views.edit_profile, name='edit_profile'),
    path('ketoan/change-password/', thu_phi_views.change_password, name='change_password'),
]