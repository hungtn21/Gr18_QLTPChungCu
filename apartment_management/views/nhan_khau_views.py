from django.shortcuts import render, redirect
from ..models import HoGiaDinh, DanCu, TamTruTamVang, NguoiDung
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash, logout
from django.contrib import messages
from django.contrib.auth.forms import PasswordChangeForm
from functools import wraps
from ..forms import EditProfileForm
from datetime import datetime
from django.db.models import Q


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

    return render(request, 'nhan_khau/change_password.html', {'form': form})

#---------------------------------Chỉnh sửa thông tin cá nhân----------------------------------------
@login_required
def edit_profile(request):
    try:
        nguoi_dung = request.user.nguoidung
    except NguoiDung.DoesNotExist:
        messages.error(request, "Không tìm thấy thông tin người dùng")
        return redirect('BQLCCDashboard')

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
            return redirect('nhan_khau_edit_profile')
    else:
        form = EditProfileForm(instance=nguoi_dung)

    return render(request, 'nhan_khau/edit_profile.html', {'form': form})

@login_required
def logout_view(request):
    logout(request)
    return redirect('login')  # 'login' là tên URL pattern cho trang đăng nhập

@login_required
@role_required('BQL Chung cư')
def thongKeDoTuoi(request):
    results =[]
    if request.method == "GET" and 'submit' in request.GET:
        gioi_tinh = request.GET.get('gender')
        tuoi_from = request.GET.get('ageFrom')
        tuoi_to = request.GET.get('ageTo')
        date_from = request.GET.get('fromDate')
        date_to = request.GET.get('toDate')
        
        queryset = DanCu.objects.all()

        if gioi_tinh:
            queryset = queryset.filter(gioi_tinh=gioi_tinh)
            
        if tuoi_from and tuoi_to:
            tuoi_from = int(tuoi_from)
            tuoi_to = int(tuoi_to)
            current_year = datetime.today().year
            nam_sinh_from = current_year - tuoi_to
            nam_sinh_to = current_year - tuoi_from
            queryset = queryset.filter(ngay_sinh__year__gte=nam_sinh_from, ngay_sinh__year__lte=nam_sinh_to)
            
        # Lọc theo khoảng thời gian từng sinh sống trong đó
        if date_from and date_to:
            # Lọc theo khoảng giao nhau: ai đã ở bất kỳ lúc nào trong khoảng này
            queryset = queryset.filter(
                Q(thoi_gian_chuyen_di__isnull=True) | Q(thoi_gian_chuyen_di__gte=date_from),
                thoi_gian_chuyen_den__lte=date_to
            )
        results = queryset

    return render(request, 'nhan_khau/thongke_do_tuoi.html', {'results': results})

@login_required 
@role_required('BQL Chung cư')
def thongKeTamTru(request):
    results = []
    total = 0

    loai_code = request.GET.get('loai') 
    from_date_str = request.GET.get('fromDate')
    to_date_str = request.GET.get('toDate')

    # Map số sang loại
    loai_mapping = {
        '1': 'Tạm trú',
        '2': 'Tạm vắng'
    }
    loai = loai_mapping.get(loai_code)

    if loai and from_date_str and to_date_str:
        try:
            from_date = datetime.strptime(from_date_str, '%Y-%m-%d').date()
            to_date = datetime.strptime(to_date_str, '%Y-%m-%d').date()

            # Queryset tách riêng để dễ kiểm soát và test
            queryset = TamTruTamVang.objects.filter(
                Q(loai_tttv=loai) &
                Q(thoi_gian_bat_dau__lte=to_date) &
                Q(thoi_gian_ket_thuc__gte=from_date)
            )

            results = queryset
            total = queryset.count()
            

        except ValueError as ve:
            print("LỖI PARSE NGÀY:", ve)
        
    context = {
        'results': results,
        'total': total,
        'request': request
        }

    return render(request, 'nhan_khau/thongke_tam_tru.html', context)


@login_required
@role_required('BQL Chung cư')
def thongKeBienDong(request):
    danh_sach_chuyen_den = []
    danh_sach_chuyen_di = []
    danh_sach_qua_doi = []
    chuyen_den = 0
    chuyen_di = 0
    qua_doi = 0
    tong_bien_dong = None

    date_from_str = request.GET.get('date_from')
    date_to_str = request.GET.get('date_to')

    if request.method == "GET" and (date_from_str or date_to_str):
        try:
            date_from = datetime.strptime(date_from_str, "%Y-%m-%d").date() if date_from_str else datetime.min.date()
            date_to = datetime.strptime(date_to_str, "%Y-%m-%d").date() if date_to_str else datetime.max.date()

            queryset_chuyen_den = DanCu.objects.filter(thoi_gian_chuyen_den__range=(date_from, date_to))
            queryset_chuyen_di = DanCu.objects.filter(thoi_gian_chuyen_di__range=(date_from, date_to))
            queryset_qua_doi = DanCu.objects.filter(trang_thai='Đã qua đời', thoi_gian_chuyen_di__range=(date_from, date_to))

            chuyen_den = queryset_chuyen_den.count()
            chuyen_di = queryset_chuyen_di.count()
            qua_doi = queryset_qua_doi.count()

            danh_sach_chuyen_den = queryset_chuyen_den
            danh_sach_chuyen_di = queryset_chuyen_di
            danh_sach_qua_doi = queryset_qua_doi

            tong_bien_dong = chuyen_den + chuyen_di + qua_doi

        except Exception as e:
            print(f"[DEBUG] Lỗi khi xử lý thống kê biến động: {e}")

    context = {
        'chuyen_den': chuyen_den,
        'chuyen_di': chuyen_di,
        'qua_doi': qua_doi,
        'tong_bien_dong': tong_bien_dong,
        'danh_sach_chuyen_den': danh_sach_chuyen_den,
        'danh_sach_chuyen_di': danh_sach_chuyen_di,
        'danh_sach_qua_doi': danh_sach_qua_doi,
        'date_from': date_from_str,
        'date_to': date_to_str,
    }

    return render(request, 'nhan_khau/thongke_bien_dong.html', context)

@login_required
@role_required('BQL Chung cư')
def lichSuThayDoi(request):
    bien_dong = []
    so_can_ho = request.GET.get('so_can_ho')
    start_date_raw = request.GET.get('start_date')
    end_date_raw = request.GET.get('end_date')

    print(f"Request params - so_can_ho: {so_can_ho}, start_date_raw: {start_date_raw}, end_date_raw: {end_date_raw}")
    
    start_date = datetime.strptime(start_date_raw, "%Y-%m-%d").date() if start_date_raw else datetime.min.date()
    end_date = datetime.strptime(end_date_raw, "%Y-%m-%d").date() if end_date_raw else datetime.max.date()


    if so_can_ho:
        try:
            ho_gia_dinh = HoGiaDinh.objects.filter(so_can_ho=so_can_ho).first()

            if not ho_gia_dinh:
                messages.error(request, "Không tìm thấy hộ gia đình với số căn hộ này.")
                return render(request, 'nhan_khau/lichsu_thaydoi.html', {'bien_dong': [], 'so_can_ho': so_can_ho})
            danh_sach_dancu = DanCu.objects.filter(ho_gia_dinh=ho_gia_dinh)

            for dancu in danh_sach_dancu:
                # Chuyển đến
                if start_date <= dancu.thoi_gian_chuyen_den <= end_date:
                    bien_dong.append({
                        'ho_ten': dancu.ho_ten,
                        'ma_can_cuoc': dancu.ma_can_cuoc,
                        'gioi_tinh': dancu.gioi_tinh,
                        'ngay_sinh': dancu.ngay_sinh,
                        'tuoi': dancu.tinh_tuoi(),
                        'loai_bien_dong': 'Chuyển đến',
                        'ngay': dancu.thoi_gian_chuyen_den,
                    })

                # Chuyển đi hoặc đã mất
                if dancu.thoi_gian_chuyen_di and start_date <= dancu.thoi_gian_chuyen_di <= end_date:
                    loai_bd = 'Đã mất' if dancu.trang_thai == 'Đã qua đời' else 'Chuyển đi'
                    bien_dong.append({
                        'ho_ten': dancu.ho_ten,
                        'ma_can_cuoc': dancu.ma_can_cuoc,
                        'gioi_tinh': dancu.gioi_tinh,
                        'ngay_sinh': dancu.ngay_sinh,
                        'tuoi': dancu.tinh_tuoi(),
                        'loai_bien_dong': loai_bd,
                        'ngay': dancu.thoi_gian_chuyen_di,
                    })

            # Sắp xếp theo ngày gần nhất
            bien_dong.sort(key=lambda x: x['ngay'], reverse=True)

        except Exception as e:
            messages.error(request, "Đã xảy ra lỗi khi truy xuất dữ liệu.")

    context = {
        'bien_dong': bien_dong,
        'so_can_ho': so_can_ho,
        'start_date': start_date_raw,
        'end_date': end_date_raw,
    }
    return render(request, 'nhan_khau/lichsu_thaydoi.html', context)

