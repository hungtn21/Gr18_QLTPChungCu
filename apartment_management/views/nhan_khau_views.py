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
from apartment_management.forms import HoGiaDinhForm


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
            form.save()
            return JsonResponse({'success': True})
        return JsonResponse({'success': False, 'html': render_to_string('nhan_khau/ho_khau_form.html', {'form': form}, request=request)})
    else:
        form = HoGiaDinhForm()
        return render(request, 'nhan_khau/ho_khau_form.html', {'form': form})


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

@login_required
@role_required('BQL Chung cư')
def create_nhankhau(request):
    if request.method == 'POST':
        form = KhoanThuCreateForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Thêm khoản thu mới thành công!')
            return redirect('view_list_khoanthu')
    else:
        form = KhoanThuCreateForm()

    return render(request, 'thu_phi/create_khoanthu.html', {'form': form})
