
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, update_session_auth_hash, logout
from django.contrib import messages
from ..models import NguoiDung,User
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import redirect
from functools import wraps
from django.contrib.auth.forms import PasswordChangeForm
from django.views.decorators.cache import never_cache
import secrets
import string
from email.message import EmailMessage
import ssl
import smtplib
from ..forms import EditProfileForm
from django.http import JsonResponse

def role_required(required_role):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if request.user.is_authenticated:
                nguoi_dung = getattr(request.user, 'nguoidung', None)
                if nguoi_dung and nguoi_dung.vai_tro == required_role:
                    return view_func(request, *args, **kwargs)
            return redirect('login')  
        return _wrapped_view
    return decorator


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            try:
                nguoi_dung = NguoiDung.objects.get(user=user)
                if nguoi_dung.vai_tro == 'BQL Chung cư':
                    return redirect('BQLCCDashboard')
                elif nguoi_dung.vai_tro == 'Kế toán':
                    return redirect('KTDashboard')
                elif nguoi_dung.vai_tro == 'Quản trị hệ thống':
                    return redirect('AdminDashboard')
                else:
                    messages.error(request, "Không xác định được vai trò người dùng.")
                    return redirect('login')
            except NguoiDung.DoesNotExist:
                messages.error(request, "Không tìm thấy thông tin người dùng.")
                return redirect('login')
        else:
            messages.error(request, "Tên đăng nhập hoặc mật khẩu không đúng.")
            return redirect('login')

    return render(request, 'nguoi_dung/login.html')

@login_required
@role_required('BQL Chung cư')
def bqlcc_dashboard(request):
    return render(request, 'nhan_khau/BQLCCDashboard.html')

@login_required
@role_required('Kế toán')
def kt_dashboard(request):
    username = request.user.username
    return render(request, 'nguoi_dung/KTDashboard.html', {'username': username})

@login_required
@role_required('Quản trị hệ thống')
def admin_dashboard(request):
    return render(request, 'nguoi_dung/AdminDashboard.html')



@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Cập nhật session để không bị đăng xuất
            messages.success(request, 'Mật khẩu đã được thay đổi thành công.')
            return redirect('admin_change_password')
        else:
            messages.error(request, 'Vui lòng kiểm tra lại thông tin.')
    else:
        form = PasswordChangeForm(request.user)

    return render(request, 'thu_phi/change_password.html', {'form': form})

#---------------------------------Chỉnh sửa thông tin cá nhân----------------------------------------
@login_required
def edit_profile(request):
    try:
        nguoi_dung = request.user.nguoidung
    except NguoiDung.DoesNotExist:
        messages.error(request, "Không tìm thấy thông tin người dùng")
        return redirect('admin_dashboard')

    if request.method == 'POST':
        form = EditProfileForm(request.POST, instance=nguoi_dung)
        if form.is_valid():
            # Cập nhật thông tin User
            ho_ten = form.cleaned_data.get('ho_ten', '').split()
            request.user.last_name = ' '.join(ho_ten[:-1]) if len(ho_ten) > 1 else ''
            request.user.first_name = ho_ten[-1] if ho_ten else ''
            request.user.email = form.cleaned_data.get('email', '')
            request.user.save()
            
            # Chỉ cập nhật số điện thoại
            nguoi_dung.so_dien_thoai = form.cleaned_data.get('so_dien_thoai', '')
            nguoi_dung.save()
            
            messages.success(request, 'Cập nhật thông tin thành công!')
            return redirect('admin_edit_profile')
    else:
        form = EditProfileForm(instance=nguoi_dung)

    return render(request, 'thu_phi/edit_profile.html', {'form': form})


@login_required
def logout_view(request):
    logout(request)
    return redirect('login')