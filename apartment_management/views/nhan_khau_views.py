# apartment_management/views/nhan_khau_views.py
from django.shortcuts import render, redirect
from apartment_management.models import DanCu  # Nhập model DanCu để lưu dữ liệu vào database
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from .nguoi_dung_views import role_required
from ..models import ChiTietThu, DanCu, DotThu, HoGiaDinh, KhoanThu
from django.db.models import Count, Q
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from ..forms import  KhoanNopCreateForm, KhoanThuCreateForm, KhoanThuForm
from django.utils.dateparse import parse_date
from django.http import HttpResponse, JsonResponse
from apartment_management.forms import HoGiaDinhForm, DanCuForm
from django.views.decorators.http import require_http_methods
from django.views.decorators.http import require_POST
from apartment_management.forms import EditProfileForm
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from apartment_management.forms import EditProfileForm
from datetime import date
from django.urls import reverse
from django import forms



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

    ho.id_chu_ho = dan_cu
    ho.save()

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

    so_can_ho = ho.so_can_ho  # ⬅️ Lưu trước khi xóa để không bị lỗi

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
        form = HoGiaDinhForm(instance=ho)  # không gán mặc định ở đây
        if form.is_valid():
            form.save()
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

    # Không cho phép xoá chủ hộ
    if ho.id_chu_ho_id == dan_cu.id:
        messages.error(request, 'Bạn không thể xoá chủ hộ.')
        return redirect(next_url or 'sua_ho_khau', pk=ho.id)

    # Xoá nếu không phải chủ hộ
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

