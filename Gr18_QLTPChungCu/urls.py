"""
URL configuration for Gr18_QLTPChungCu project.
"""

from django.contrib import admin
from django.urls import path
from django.shortcuts import redirect
from apartment_management.views import nguoi_dung_views, nhan_khau_views, thu_phi_views

urlpatterns = [
    # Authentication & Dashboards
    path('login/', nguoi_dung_views.login_view, name='login'),
    path('', lambda request: redirect('login')),
    path('admin/user-management/', nguoi_dung_views.login_view, name='admin-user-management'),
    path('logout/', nguoi_dung_views.logout_view, name='admin_logout'),
    path('dashboard/admin/', nguoi_dung_views.admin_dashboard, name='AdminDashboard'),
    path('dashboard/bqlcc/', nguoi_dung_views.bqlcc_dashboard, name='BQLCCDashboard'),
    path('dashboard/ketoan/', nguoi_dung_views.kt_dashboard, name='KTDashboard'),

    # Kế toán - Đợt thu
    path('ketoan/view-list-dot-thu/', thu_phi_views.list_dot_thu_view, name='list_dot_thu'),
    path('ketoan/dot-thu-details/<int:dot_id>/', thu_phi_views.chi_tiet_dot_thu_view, name='detail_dot_thu'),
    path('ketoan/dot-thu/edit/<int:dot_id>/', thu_phi_views.sua_dot_thu_view, name='edit_dot_thu'),
    path('ketoan/dot-thu/delete/<int:dot_id>/', thu_phi_views.xoa_dot_thu_view, name='xoa_dot_thu'),
    path('ketoan/dot-thu/create/', thu_phi_views.tao_dot_thu_view, name='tao_dot_thu_view'),

    # Kế toán - Khoản thu
    path('api/khoan-thu/', thu_phi_views.api_khoan_thu_list, name='api_khoan_thu_list'),
    path('ketoan/view-list-khoanthu', thu_phi_views.view_list_khoanthu, name='view_list_khoanthu'),
    path('ketoan/create-khoanthu', thu_phi_views.create_khoanthu, name='create_khoanthu'),
    path('ketoan/update-khoanthu/<int:pk>', thu_phi_views.update_khoanthu, name='update_khoanthu'),
    path('ketoan/delete-khoanthu/<int:pk>', thu_phi_views.delete_khoanthu, name='delete_khoanthu'),

    # Kế toán - Khoản nộp
    path('ketoan/view-list-khoannop', thu_phi_views.view_list_khoannop, name='view_list_khoannop'),
    path('ketoan/khoannop-details/<int:pk>', thu_phi_views.khoannop_details, name='khoannop_details'),

    # Kế toán - Tài khoản
    path('ketoan/edit-profile/', thu_phi_views.edit_profile, name='edit_profile'),
    path('ketoan/change-password/', thu_phi_views.change_password, name='change_password'),
]
