
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from ..models import NguoiDung
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import redirect
from functools import wraps

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
    return render(request, 'thu_phi/KTDashboard.html')

@login_required
@role_required('Quản trị hệ thống')
def admin_dashboard(request):
    return render(request, 'nguoi_dung/AdminDashboard.html')