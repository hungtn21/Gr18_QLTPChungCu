
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, update_session_auth_hash, logout
from django.contrib.auth import authenticate, login, update_session_auth_hash, logout
from django.contrib import messages
from ..models import NguoiDung,User
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
import re



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

@never_cache
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
                    return redirect('admin_user_management')
                else:
                    messages.error(request, "Không xác định được vai trò người dùng.")
            except NguoiDung.DoesNotExist:
                messages.error(request, "Không tìm thấy thông tin người dùng.")
        else:
            messages.error(request, "Tên đăng nhập hoặc mật khẩu không đúng.")
        
        return redirect('login')  # Thực hiện redirect để đảm bảo thông báo được hiển thị và toast được kích hoạt.

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

# @login_required
# @role_required('Quản trị hệ thống')
# def admin_dashboard(request):
#     return render(request, 'nguoi_dung/AdminDashboard.html')


#---------------------------Gửi password qua email--------------------------------- 

def send_password_through_email(email,password):
    email_sender = 'bluemoon.system1@gmail.com'
    email_password = 'yexb gudc yveh bgjm'
    email_receiver = email
    subject = "Thông báo: Đăng ký thành công tài khoản hệ thống quản lý Chung cư Bluemoon"
    body = "Mật khẩu của bạn là: {password}. Hãy tiến hành đổi mật khẩu sau khi đăng nhập.".format(password=password)

    em = EmailMessage()
    em['From'] = email_sender
    em['To'] = email_receiver
    em['Subject'] = subject
    em.set_content(body)

    context = ssl.create_default_context()

    with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
        smtp.login(email_sender, email_password)
        smtp.sendmail(email_sender, email_receiver, em.as_string())

#------------------------------Tạo người dùng mới--------------------------------------------

@login_required
@role_required('Quản trị hệ thống')
def create_new_user(request):
    if request.method == 'POST':
        try:
            # Lấy dữ liệu từ form
            ho_ten = request.POST.get('ho_ten')
            email = request.POST.get('email')
            ten_dang_nhap = request.POST.get('ten_dang_nhap')
            so_dien_thoai = request.POST.get('so_dien_thoai')
            vai_tro = request.POST.get('vai_tro')
            
            # Kiểm tra username/email tồn tại
            
            if not all([ho_ten, email, ten_dang_nhap, so_dien_thoai, vai_tro]):
                messages.error(request, 'Vui lòng điền đầy đủ thông tin')
                return redirect('create_new_user')
                
            if User.objects.filter(username=ten_dang_nhap).exists():
                messages.error(request, 'Tên đăng nhập đã tồn tại!')
                return redirect('create_new_user')
            
            if not re.match(r'^[0-9]{10,15}$', so_dien_thoai):
                messages.error(request, 'Số điện thoại không hợp lệ')
                return redirect('create_new_user')
                
            if User.objects.filter(email=email).exists():
                messages.error(request, 'Email đã được sử dụng!')
                return redirect('create_new_user')
            
            # Tạo mật khẩu ngẫu nhiên (8-12 ký tự, có chữ hoa, chữ thường, số)
            alphabet = string.ascii_letters + string.digits
            password = ''.join(secrets.choice(alphabet) for _ in range(secrets.choice(range(8, 13))))
            print(password)
            # Tạo user mới với mật khẩu ngẫu nhiên
            user = User.objects.create_user(
                username=ten_dang_nhap,
                email=email,
                password=password,  # Django sẽ tự mã hóa
                first_name=ho_ten.split()[-1],
                last_name=' '.join(ho_ten.split()[:-1])
            )
            
            # Tạo NguoiDung liên kết
            NguoiDung.objects.create(
                user=user,
                vai_tro=vai_tro,
                so_dien_thoai=so_dien_thoai,
                trang_thai='Đang hoạt động'
            )
            send_password_through_email(email,password)
            messages.success(request, 'Tạo tài khoản thành công!')
            return redirect('create_new_user')
            
        except Exception as e:
            messages.error(request, f'Có lỗi xảy ra: {str(e)}')
            return redirect('create_new_user')
    
    return render(request, 'nguoi_dung/create_new_user.html')

#--------------------------------------Thay đổi mật khẩu---------------------------------------

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

    return render(request, 'nguoi_dung/change_password.html', {'form': form})

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

    return render(request, 'nguoi_dung/edit_profile.html', {'form': form})

@login_required
def logout_view(request):
    logout(request)
    return redirect('login')  # 'login' là tên URL pattern cho trang đăng nhập

#----------------------------------------Quản lý người dùng-------------------------------------------
@login_required
@role_required('Quản trị hệ thống')
def user_management(request):
    # Lấy danh sách người dùng
    users = User.objects.select_related('nguoidung').all().order_by('-date_joined')
    
    # Chuẩn bị dữ liệu cho template
    user_list = []
    stt = 1  # Bắt đầu từ 1
    for user in users:
        try:
            nguoi_dung = user.nguoidung
            user_list.append({
                'stt': stt,
                'id': user.id,
                'username': user.username,
                'ho_ten': f"{user.last_name} {user.first_name}".strip(),
                'email': user.email,
                'so_dien_thoai': nguoi_dung.so_dien_thoai,
                'trang_thai': nguoi_dung.trang_thai,
                'vai_tro': nguoi_dung.vai_tro,
            })
            stt += 1  # Chỉ tăng khi đã append
        except NguoiDung.DoesNotExist:
            continue
            
    
    context = {
        'users': user_list
    }
    return render(request, 'nguoi_dung/user_management.html', context)

@login_required
@role_required('Quản trị hệ thống')
def toggle_user_status(request, user_id):
    if request.method == 'POST':
        try:
            user = User.objects.get(id=user_id)
            nguoi_dung = user.nguoidung
            if nguoi_dung.trang_thai == 'Đang hoạt động':
                nguoi_dung.trang_thai = 'Bị khóa'
                action = 'locked'
            else:
                nguoi_dung.trang_thai = 'Đang hoạt động'
                action = 'unlocked'
            nguoi_dung.save()
            return JsonResponse({'status': 'success', 'action': action, 'new_status': nguoi_dung.trang_thai})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)