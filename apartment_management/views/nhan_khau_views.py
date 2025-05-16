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


@login_required
@role_required('BQL Chung cư')
def quan_ly_ho_khau(request):
    query = request.GET.get('q', '').strip()

    # Annotate: thêm cột đếm số thành viên đang sinh sống
    ho_khau_list = HoGiaDinh.objects.annotate(
        tong_thanh_vien=Count('dancu', filter=Q(dancu__trang_thai='Đang sinh sống'))
    )

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
            ho_gia_dinh = form.save()
            messages.success(request, 'Tạo hộ khẩu thành công! Vui lòng thêm nhân khẩu.')
            return redirect('them_nhan_khau_cho_ho', ho_gia_dinh_id=ho_gia_dinh.id)
    else:
        form = HoGiaDinhForm()

    return render(request, 'nhan_khau/create_hokhau.html', {'form': form})

@login_required
@role_required('BQL Chung cư')
def them_nhan_khau_cho_ho(request, ho_gia_dinh_id):
    ho = get_object_or_404(HoGiaDinh, id=ho_gia_dinh_id)
    dancu_list = DanCu.objects.filter(ho_gia_dinh=ho)

    if request.method == 'POST':
        form = DanCuForm(request.POST)
        if form.is_valid():
            dan_cu = form.save(commit=False)
            dan_cu.ho_gia_dinh = ho
            dan_cu.save()

            # ✅ Gán chủ hộ nếu chưa có
            if not ho.id_chu_ho:
                ho.id_chu_ho = dan_cu
                ho.save()

            messages.success(request, 'Đã thêm nhân khẩu.')
            return redirect('them_nhan_khau_cho_ho', ho_gia_dinh_id=ho.id)
    else:
        form = DanCuForm(initial={'thoi_gian_chuyen_den': ho.thoi_gian_bat_dau_o})  # ✅ Set giá trị mặc định

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
    ho.delete()  # ✅ Xóa HoGiaDinh, đồng thời xóa luôn DanCu liên kết
    messages.success(request, f'Đã xóa hộ khẩu căn hộ {ho.so_can_ho}.')
    return redirect('quan_ly_ho_khau')

@login_required
@role_required('BQL Chung cư')
def sua_ho_khau(request, pk):
    ho = get_object_or_404(HoGiaDinh, id=pk)
    dancu_list = DanCu.objects.filter(ho_gia_dinh=ho)

    if request.method == 'POST':
        form = HoGiaDinhForm(request.POST, instance=ho)
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
    })
@login_required
@role_required('BQL Chung cư')
@require_http_methods(["POST"])
def xoa_nhan_khau(request, pk):
    dan_cu = get_object_or_404(DanCu, id=pk)
    ho = dan_cu.ho_gia_dinh
    is_chu_ho = (ho.id_chu_ho_id == dan_cu.id)

    dancu_trong_ho = DanCu.objects.filter(ho_gia_dinh=ho)

    if dancu_trong_ho.count() <= 1:
        messages.error(request, 'Không thể xóa. Hộ khẩu phải có ít nhất một nhân khẩu.')
        return redirect('sua_ho_khau', pk=ho.id)

    dan_cu.delete()

    # Nếu người bị xóa là chủ hộ → chuyển chủ hộ cho người khác
    if is_chu_ho:
        dancu_con_lai = DanCu.objects.filter(ho_gia_dinh=ho).order_by('ngay_sinh')
        if dancu_con_lai.exists():
            ho.id_chu_ho = dancu_con_lai.first()
        else:
            ho.id_chu_ho = None
        ho.save()

    messages.success(request, 'Đã xóa nhân khẩu.')
    return redirect('sua_ho_khau', pk=ho.id)  # ✅ luôn quay lại trang sửa hộ khẩu


@login_required
@role_required('BQL Chung cư')
def sua_nhan_khau(request, pk):
    dan_cu = get_object_or_404(DanCu, id=pk)
    ho = dan_cu.ho_gia_dinh

    if request.method == 'POST':
        form = DanCuForm(request.POST, instance=dan_cu)
        if form.is_valid():
            form.save()
            messages.success(request, 'Cập nhật thông tin nhân khẩu thành công.')
            return redirect('sua_ho_khau', pk=ho.id)
    else:
        form = DanCuForm(instance=dan_cu)

    return render(request, 'nhan_khau/sua_nhan_khau.html', {
        'form': form,
        'ho': ho,
        'dan_cu': dan_cu
    })

@login_required
@role_required('BQL Chung cư')
def them_nhan_khau_tu_sua(request, ho_id):
    ho = get_object_or_404(HoGiaDinh, id=ho_id)

    if request.method == 'POST':
        form = DanCuForm(request.POST)
        if form.is_valid():
            dancu = form.save(commit=False)
            dancu.ho_gia_dinh = ho
            dancu.save()

            # Nếu hộ chưa có chủ hộ → gán người này
            if not ho.id_chu_ho:
                ho.id_chu_ho = dancu
                ho.save()

            messages.success(request, f'Đã thêm nhân khẩu cho căn hộ {ho.so_can_ho}.')
            return redirect('sua_ho_khau', pk=ho.id)
    else:
        form = DanCuForm(initial={'thoi_gian_chuyen_den': ho.thoi_gian_bat_dau_o})

    return render(request, 'nhan_khau/them_nhan_khau_tu_sua.html', {
        'form': form,
        'ho': ho
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
    trang_thai = request.POST.get('trang_thai')
    thoi_gian_chuyen_den = request.POST.get('thoi_gian_chuyen_den')
    thoi_gian_chuyen_di = request.POST.get('thoi_gian_chuyen_di') or None  # có thể để trống

    # Tạo đối tượng DanCu mới
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

        # Nếu hộ chưa có chủ hộ, gán luôn người này
        if ho.id_chu_ho is None:
            ho.id_chu_ho = dan_cu
            ho.save()

        messages.success(request, f'Đã thêm nhân khẩu: {dan_cu.ho_ten}')
    except Exception as e:
        messages.error(request, f'Lỗi khi thêm nhân khẩu: {str(e)}')

    return redirect('sua_ho_khau', pk=ho.id)

@login_required
@role_required('BQL Chung cư')
def quan_ly_nhan_khau(request):
    query = request.GET.get('q')
    if query:
        nhan_khau_list = DanCu.objects.filter(
            Q(ho_ten__icontains=query) |
            Q(ma_can_cuoc__icontains=query) |
            Q(ho_gia_dinh__icontains=query)
        )
    else:
        nhan_khau_list = DanCu.objects.all()

    return render(request, 'nhan_khau/quan_ly_nhan_khau.html', {
        'nhan_khau_list': nhan_khau_list,
        'query': query or ''
    })

