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
    
    #========================== QLCC routes=========================================================
    
    path('thongke_do_tuoi/', nhan_khau_views.thongKeDoTuoi, name='thongKeDoTuoi'),
    path('thongke_tam_tru/', nhan_khau_views.thongKeTamTru, name='thongKeTamTru'),
    path('thongke_bien_dong/', nhan_khau_views.thongKeBienDong, name='thongKeBienDong'),
    path('lichsu_thaydoi/', nhan_khau_views.lichSuThayDoi, name='lichSuThayDoi'),
    path('bqlcc/change-password/', nhan_khau_views.change_password, name='nhan_khau_change_password'),
    path('bqlcc/edit-profile/', nhan_khau_views.edit_profile, name='nhan_khau_edit_profile'),
]