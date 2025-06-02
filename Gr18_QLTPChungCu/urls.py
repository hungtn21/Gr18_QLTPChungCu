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
    #==========================Admin routes=========================================================
    path('admin/user-management/', nguoi_dung_views.user_management, name='admin_user_management'),
    path('admin/user-management/create-new-user', nguoi_dung_views.create_new_user, name='create_new_user'),
    path('admin/change-password/', nguoi_dung_views.change_password, name='admin_change_password'),
    path('admin/edit-profile/', nguoi_dung_views.edit_profile, name='admin_edit_profile'),
    path('logout/', nguoi_dung_views.logout_view, name='admin_logout'),
    # path('dashboard/admin/', nguoi_dung_views.admin_dashboard, name='AdminDashboard'),
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
    path('admin/user-management/toggle-status/<int:user_id>/', nguoi_dung_views.toggle_user_status, name='toggle_user_status'),
    #==========================Ke toan routes=========================================================
    path('ketoan/view-list-khoanthu', thu_phi_views.view_list_khoanthu, name='view_list_khoanthu'),
    path('ketoan/create-khoanthu', thu_phi_views.create_khoanthu, name='create_khoanthu'),
    path('ketoan/update-khoanthu/<int:pk>', thu_phi_views.update_khoanthu, name='update_khoanthu'),
    path('ketoan/delete-khoanthu/<int:pk>', thu_phi_views.delete_khoanthu, name='delete_khoanthu'),
    path('ketoan/view-list-khoannop', thu_phi_views.view_list_khoannop, name='view_list_khoannop'),
    path('ketoan/khoannop-details/<int:pk>', thu_phi_views.khoannop_details, name='khoannop_details'),
    path('ketoan/edit-profile', thu_phi_views.edit_profile, name ='kt_edit_profile'),
    path('ketoan/change-password', thu_phi_views.change_password, name ='kt_change_password'),

    
#========================== QLCC routes=========================================================
    
    path('thongke_do_tuoi/', nhan_khau_views.thongKeDoTuoi, name='thongKeDoTuoi'),
    path('thongke_tam_tru/', nhan_khau_views.thongKeTamTru, name='thongKeTamTru'),
    path('thongke_bien_dong/', nhan_khau_views.thongKeBienDong, name='thongKeBienDong'),
    path('lichsu_thaydoi/', nhan_khau_views.lichSuThayDoi, name='lichSuThayDoi'),
    path('bqlChungCu/quan-ly-nhan-khau/', nhan_khau_views.quan_ly_nhan_khau, name='quan_ly_nhan_khau'),
    path('bqlChungCu/quan_ly_ho_khau', nhan_khau_views.quan_ly_ho_khau, name='quan_ly_ho_khau'),
    path('bqlChungCu/edit-profile/',nhan_khau_views.edit_profile, name='nhankhau_edit_profile'),
    path('bqlChungCu/change-password/', nhan_khau_views.change_password, name='nhankhau_change_password'),
    path('bqlChungCu/quan_ly_ho_khau/create/', nhan_khau_views.create_ho_khau, name='create_ho_khau'),
    path('bqlChungCu/doi-chu-ho/<int:ho_id>/<int:dan_cu_id>/',nhan_khau_views.doi_chu_ho,name='doi_chu_ho'),
    path('bqlChungCu/xoa-ho-khau/<int:pk>/', nhan_khau_views.xoa_ho_khau, name='xoa_ho_khau'),
    path('bqlChungCu/sua-ho-khau/<int:pk>/', nhan_khau_views.sua_ho_khau, name='sua_ho_khau'),
    path('bqlChungCu/sua-nhan-khau/<int:pk>/', nhan_khau_views.sua_nhan_khau, name='sua_nhan_khau'),
    path('bqlChungCu/tam-tru-tam-vang/<int:pk>/', nhan_khau_views.tam_tru_tam_vang, name='tam_tru_tam_vang'),
    path('bqlChungCu/xoa-nhan-khau/<int:pk>/', nhan_khau_views.xoa_nhan_khau, name='xoa_nhan_khau'),
    path('bqlChungCu/them-nhan-khau-modal/<int:ho_id>/', nhan_khau_views.them_nhan_khau_tu_modal, name='them_nhan_khau_tu_modal'),
    path('bqlChungCu/tach-ho/<int:ho_id>/', nhan_khau_views.tach_ho, name='tach_ho'),
    path('them-phuong-tien/<int:ho_id>/', nhan_khau_views.them_phuong_tien, name='them_phuong_tien'),
    path('xoa-phuong-tien/<int:pt_id>/', nhan_khau_views.xoa_phuong_tien, name='xoa_phuong_tien'),
    # Kế toán - Khoản nộp
    path('ketoan/view-list-khoannop', thu_phi_views.view_list_khoannop, name='view_list_khoannop'),
    path('ketoan/khoannop-details/<int:pk>', thu_phi_views.khoannop_details, name='khoannop_details'),

    # Kế toán - Tài khoản
    path('ketoan/edit-profile/', thu_phi_views.edit_profile, name='edit_profile'),
    path('ketoan/change-password/', thu_phi_views.change_password, name='change_password'),
]
