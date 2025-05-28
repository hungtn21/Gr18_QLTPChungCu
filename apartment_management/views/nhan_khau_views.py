from datetime import date, datetime
from functools import wraps

from django import forms
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.db.models import Count, Q
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.utils.dateparse import parse_date
from django.views.decorators.http import require_http_methods, require_POST

from apartment_management.models import DanCu, ChiTietThu, DotThu, HoGiaDinh, KhoanThu, TamTruTamVang, NguoiDung
from apartment_management.forms import (
    DanCuForm, HoGiaDinhForm, EditProfileForm,
    KhoanThuCreateForm, KhoanThuForm, KhoanNopCreateForm
)
from .nguoi_dung_views import role_required
@login_required
@role_required('BQL Chung cư')
def quan_ly_ho_khau(request):
    query = request.GET.get('q', '').strip()

    # Annotate: thêm cột đếm số thành viên đang sinh sống
    ho_khau_list = HoGiaDinh.objects.annotate(
        tong_thanh_vien=Count('dancu', filter=Q(dancu__trang_thai='Đang sinh sống'))
    ).order_by('id')

    if query:
        ho_khau_list = ho_khau_list.filter(
            Q(id__icontains=query) |
            Q(id_chu_ho__ho_ten__icontains=query) |
            Q(id_chu_ho__ma_can_cuoc__icontains=query) |
            Q(so_can_ho__icontains=query) |
            Q(thoi_gian_bat_dau_o__icontains=query) |
            Q(tong_thanh_vien__icontains=query)
        )

    return render(request, 'nhan_khau/quan_ly_ho_khau.html', {
        'ho_khau_list': ho_khau_list,
        'query': query
    })

@login_required
@role_required('BQL Chung cư')
def create_ho_khau(request):
    if request.method == 'POST':
        form = HoGiaDinhForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Tạo hộ khẩu thành công!')
            return redirect('quan_ly_ho_khau')
    else:
        form = HoGiaDinhForm(initial={'trang_thai': 'Đang ở'})

    return render(request, 'nhan_khau/create_hokhau.html', {'form': form})


@login_required
@role_required('BQL Chung cư')
def them_nhan_khau_cho_ho(request, ho_gia_dinh_id):
    ho = get_object_or_404(HoGiaDinh, id=ho_gia_dinh_id)
    dancu_list = DanCu.objects.filter(ho_gia_dinh=ho)

    if request.method == 'POST':
        form = DanCuForm(request.POST or None, hide_trang_thai=True)
        if form.is_valid():
            dan_cu = form.save(commit=False)
            dan_cu.trang_thai = 'Đang sinh sống'
            dan_cu.ho_gia_dinh = ho
            dan_cu.save()

            # Gán chủ hộ nếu chưa có
            if not ho.id_chu_ho:
                ho.id_chu_ho = dan_cu
                ho.save()

            messages.success(request, 'Đã thêm nhân khẩu.')
            return redirect('them_nhan_khau_cho_ho', ho_gia_dinh_id=ho.id)
    else:
        form = DanCuForm(initial={
    'thoi_gian_chuyen_den': ho.thoi_gian_bat_dau_o,
    'trang_thai': 'Đang sinh sống',  # gán mặc định tại đây
})


    return render(request, 'nhan_khau/them_nhan_khau.html', {
        'form': form,
        'ho': ho,
        'dancu_list': dancu_list
    })

@login_required
@role_required('BQL Chung cư')
@require_http_methods(["POST"])
def doi_chu_ho(request, ho_id, dan_cu_id):
    ho = get_object_or_404(HoGiaDinh, id=ho_id)
    dan_cu = get_object_or_404(DanCu, id=dan_cu_id, ho_gia_dinh=ho)

    # Đổi chủ hộ
    ho.id_chu_ho = dan_cu
    ho.save()

    # Làm mới đối tượng ho để đảm bảo thay đổi được cập nhật ngay
    ho.refresh_from_db()

    messages.success(request, f'Đã đổi chủ hộ thành {dan_cu.ho_ten}.')

    next_param = request.GET.get('next')
    if next_param == 'edit':
        return redirect('sua_ho_khau', pk=ho.id)
    else:
        return redirect('them_nhan_khau_cho_ho', ho_gia_dinh_id=ho.id)


@login_required
@role_required('BQL Chung cư')
@require_http_methods(["POST"])
def xoa_ho_khau(request, pk):
    ho = get_object_or_404(HoGiaDinh, id=pk)

    so_can_ho = ho.so_can_ho  #  Lưu trước khi xóa để không bị lỗi

    # Gỡ liên kết chủ hộ để tránh lỗi PROTECTED
    ho.id_chu_ho = None
    ho.save()

    # Xóa dân cư trước
    DanCu.objects.filter(ho_gia_dinh=ho).delete()

    # Xóa hộ
    ho.delete()

    # Thông báo thành công (dùng biến đã lưu)
    messages.success(request, f'Đã xóa hộ khẩu căn hộ {so_can_ho}.')
    return redirect('quan_ly_ho_khau')

@login_required
@role_required('BQL Chung cư')
def sua_ho_khau(request, pk):
    ho = get_object_or_404(HoGiaDinh, id=pk)
    dancu_list = DanCu.objects.filter(ho_gia_dinh=ho)

    if request.method == 'POST':
        form = HoGiaDinhForm(request.POST, instance=ho)
        if form.is_valid():
            ho_truoc = ho.trang_thai  # lưu trạng thái cũ
            ho = form.save()  # cập nhật hộ
            messages.success(request, 'Đã cập nhật thông tin hộ khẩu.')
            return redirect('quan_ly_ho_khau')
    else:
        form = HoGiaDinhForm(instance=ho)

    return render(request, 'nhan_khau/sua_hokhau.html', {
        'form': form,
        'ho': ho,
        'dancu_list': dancu_list,
        'today': date.today().isoformat(),
    })

@login_required
@role_required('BQL Chung cư')
@require_http_methods(["POST"])
def xoa_nhan_khau(request, pk):
    dan_cu = get_object_or_404(DanCu, id=pk)
    ho = dan_cu.ho_gia_dinh
    next_url = request.POST.get('next')

    # Nếu hiện tại là chủ hộ, không xoá
    if ho.id_chu_ho_id == dan_cu.id:
        messages.error(request, 'Bạn không thể xoá chủ hộ hiện tại.')
        return redirect(next_url or 'sua_ho_khau', pk=ho.id)

    # Nếu đã từng là chủ hộ của bất kỳ hộ nào (cũ hoặc hiện tại), hủy liên kết đó
    HoGiaDinh.objects.filter(id_chu_ho=dan_cu).update(id_chu_ho=None)
    
    # Xoá nhân khẩu
    dan_cu.delete()
    messages.success(request, 'Đã xóa nhân khẩu.')
    return redirect(next_url or 'sua_ho_khau', pk=ho.id)

@login_required
@role_required('BQL Chung cư')
def sua_nhan_khau(request, pk):
    dancu = get_object_or_404(DanCu, pk=pk)
    next_url = request.GET.get('next') or request.POST.get('next')

    if request.method == 'POST':
        form = DanCuForm(request.POST, instance=dancu)
        if form.is_valid():
            form.save()
            messages.success(request, 'Cập nhật nhân khẩu thành công.')
            return redirect(next_url or 'sua_ho_khau', pk=dancu.ho_gia_dinh.id)
    else:
        form = DanCuForm(instance=dancu)

    default_url = reverse('sua_ho_khau', args=[dancu.ho_gia_dinh.id])
    return render(request, 'nhan_khau/sua_nhan_khau.html', {
    'form': form,
    'dan_cu': dancu,
    'next': next_url,
    'default_url': default_url,
})





@login_required
@role_required('BQL Chung cư')
@require_POST
def them_nhan_khau_tu_modal(request, ho_id):
    ho = get_object_or_404(HoGiaDinh, id=ho_id)

    # Lấy dữ liệu từ POST
    ho_ten = request.POST.get('ho_ten')
    ngay_sinh = request.POST.get('ngay_sinh')
    gioi_tinh = request.POST.get('gioi_tinh')
    ma_can_cuoc = request.POST.get('ma_can_cuoc')
    so_dien_thoai = request.POST.get('so_dien_thoai')
    trang_thai = request.POST.get('trang_thai') or 'Đang sinh sống'
    thoi_gian_chuyen_den = request.POST.get('thoi_gian_chuyen_den')
    thoi_gian_chuyen_di = request.POST.get('thoi_gian_chuyen_di') or None
    #Kiểm tra CCCD đã tồn tại chưa
    if DanCu.objects.filter(ma_can_cuoc=ma_can_cuoc).exists():
        return JsonResponse({'success': False, 'message': 'CCCD đã tồn tại.'}, status=400)

    if not so_dien_thoai.isdigit() or len(so_dien_thoai) != 10:
        return JsonResponse({'success': False, 'message': 'Số điện thoại phải có đúng 10 chữ số.'}, status=400)

    if not ma_can_cuoc.isdigit() or len(ma_can_cuoc) != 12:
        return JsonResponse({'success': False, 'message': 'CCCD phải có đúng 12 chữ số.'}, status=400)

    if ngay_sinh and ngay_sinh > date.today().isoformat():
        return JsonResponse({'success': False, 'message': 'Ngày sinh không được lớn hơn ngày hiện tại.'}, status=400)
    try:
        dan_cu = DanCu.objects.create(
            ho_gia_dinh=ho,
            ho_ten=ho_ten,
            ngay_sinh=ngay_sinh,
            gioi_tinh=gioi_tinh,
            ma_can_cuoc=ma_can_cuoc,
            so_dien_thoai=so_dien_thoai,
            trang_thai=trang_thai,
            thoi_gian_chuyen_den=thoi_gian_chuyen_den,
            thoi_gian_chuyen_di=thoi_gian_chuyen_di
        )

        if ho.id_chu_ho is None:
            ho.id_chu_ho = dan_cu
            ho.save()

        return JsonResponse({'success': True, 'message': 'Đã thêm thông tin nhân khẩu thành công.'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Lỗi: {str(e)}'}, status=400)


@login_required
@role_required('BQL Chung cư')
def quan_ly_nhan_khau(request):
    query = request.GET.get('q')
    if query:
        nhan_khau_list = DanCu.objects.filter(
            Q(ho_ten__icontains=query) |
            Q(ma_can_cuoc__icontains=query) |
            Q(so_dien_thoai__icontains=query) |
            Q(ho_gia_dinh__so_can_ho__icontains=query) |
            Q(ho_gia_dinh__id_chu_ho__ho_ten__icontains=query)
    )
    else:
        nhan_khau_list = DanCu.objects.all()
    return render(request, 'nhan_khau/quan_ly_nhan_khau.html', {
        'nhan_khau_list': nhan_khau_list,
        'query': query or ''
    })
    
@login_required
@role_required('BQL Chung cư')
@require_POST
def tach_ho(request, ho_id):
    ho_cu = get_object_or_404(HoGiaDinh, id=ho_id)

    # Lấy dữ liệu từ form
    so_can_ho = request.POST.get('so_can_ho')
    dien_tich = request.POST.get('dien_tich')
    ghi_chu = request.POST.get('ghi_chu', '')
    ids_thanh_vien = request.POST.getlist('thanh_vien_ids')
    id_chu_ho_moi = request.POST.get('id_chu_ho_moi')

    #Kiểm tra trùng số căn hộ
    if HoGiaDinh.objects.filter(so_can_ho=so_can_ho).exists():
        messages.error(request, f'Căn hộ số {so_can_ho} đã tồn tại.')
        return redirect('sua_ho_khau', pk=ho_id)

    # Validate còn lại
    if not ids_thanh_vien:
        messages.error(request, 'Vui lòng chọn ít nhất một thành viên để tách.')
        return redirect('sua_ho_khau', pk=ho_id)

    if id_chu_ho_moi not in ids_thanh_vien:
        messages.error(request, 'Chủ hộ mới phải là một trong các thành viên được chọn.')
        return redirect('sua_ho_khau', pk=ho_id)

    # Tạo hộ mới
    ho_moi = HoGiaDinh.objects.create(
        so_can_ho=so_can_ho,
        dien_tich=dien_tich,
        ghi_chu=ghi_chu,
        thoi_gian_bat_dau_o=date.today().isoformat(),
        trang_thai='Đang ở',
    )

    danh_sach_dan_cu = DanCu.objects.filter(id__in=ids_thanh_vien)
    for dancu in danh_sach_dan_cu:
        dancu.ho_gia_dinh = ho_moi
        dancu.save()

    chu_ho_obj = DanCu.objects.get(id=id_chu_ho_moi)
    ho_moi.id_chu_ho = chu_ho_obj
    ho_moi.save()

    messages.success(request, f'Đã tách hộ thành công sang căn hộ {so_can_ho}.')
    return redirect('sua_ho_khau', pk=ho_id)

#--------------------------------------Thay đổi mật khẩu---------------------------------------

@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Cập nhật session để không bị đăng xuất
            messages.success(request, 'Mật khẩu đã được thay đổi thành công.')
            return redirect('change_password')
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
            return redirect('nhan_khau/edit_profile')
    else:
        form = EditProfileForm(instance=nguoi_dung)

    return render(request, 'nhan_khau/edit_profile.html', {'form': form})

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

