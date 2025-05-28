
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .nguoi_dung_views import role_required
from ..models import ChiTietThu, DanCu, DotThu, HoGiaDinh, KhoanThu
from django.db.models import Q
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from ..forms import  KhoanNopCreateForm, KhoanThuCreateForm, KhoanThuForm
from django.utils.dateparse import parse_date
from django.http import HttpResponse, JsonResponse

def xoa_tat_ca_chi_tiet_thu():
    ChiTietThu.objects.all().delete()

def xoa_chi_tiet_thu(request):
    # Xóa tất cả bản ghi trong bảng ChiTietThu
    xoa_tat_ca_chi_tiet_thu()
    return HttpResponse("Đã xóa tất cả bản ghi trong bảng ChiTietThu")

@login_required
@role_required('Kế toán')
def view_list_khoanthu(request):
    query = request.GET.get('q')
    if query:
        khoan_thu_list = KhoanThu.objects.filter(
            Q(ten_khoan_thu__icontains=query) |
            Q(loai_khoan_thu__icontains=query) |
            Q(ghi_chu__icontains=query)
        )
    else:
        khoan_thu_list = KhoanThu.objects.all()

    return render(request, 'thu_phi/view_list_khoanthu.html', {
        'khoan_thu_list': khoan_thu_list,
        'query': query or ''
    })


@login_required
@role_required('Kế toán')
def create_khoanthu(request):
    if request.method == 'POST':
        form = KhoanThuCreateForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Thêm khoản thu mới thành công!')
            return redirect('view_list_khoanthu')
    else:
        form = KhoanThuCreateForm()

    return render(request, 'thu_phi/create_khoanthu.html', {'form': form})

@login_required
@role_required('Kế toán')
def update_khoanthu(request, pk):
    khoan_thu = get_object_or_404(KhoanThu, pk=pk)
    if request.method == 'POST':
        form = KhoanThuForm(request.POST, instance=khoan_thu)
        if form.is_valid():
            form.save()
            messages.success(request, 'Cập nhật khoản thu thành công.')
            return redirect('view_list_khoanthu')  
    else:
        form = KhoanThuForm(instance=khoan_thu)
        
        

    return render(request, 'thu_phi/update_khoanthu.html', {
        'form': form,
        'khoan_thu': khoan_thu
    })

@login_required
@role_required('Kế toán')
def delete_khoanthu(request, pk):
    khoan_thu = get_object_or_404(KhoanThu, pk=pk)
    dot_thu_tien_hanh = DotThu.objects.filter(khoan_thu=khoan_thu, trang_thai='Đang tiến hành').first()

    if request.method == 'POST':
        khoan_thu.delete()
        messages.success(request, 'Xóa khoản thu thành công.')
        return redirect('view_list_khoanthu')

    context = {
        'khoan_thu': khoan_thu,
        'dot_thu_tien_hanh': dot_thu_tien_hanh,
    }
    return render(request, 'thu_phi/delete_khoanthu.html', context)



@login_required
@role_required('Kế toán')
def view_list_khoannop(request):
    query = request.GET.get('q')
    khoan_nop_info = []

    # Lọc các đợt thu đang tiến hành
    if query:
        dot_thu_list = DotThu.objects.filter(
            Q(khoan_thu__ten_khoan_thu__icontains=query) |
            Q(ten_dot_thu__icontains=query)
        )
    else:
        dot_thu_list = DotThu.objects.filter(trang_thai="Đang tiến hành")

    for dot_thu in dot_thu_list:
        # Lấy danh sách các hộ đang sinh sống (dựa theo DanCu)
        ho_dang_sinh_song_ids = DanCu.objects.filter(trang_thai='Đang sinh sống')\
                                             .values_list('ho_gia_dinh_id', flat=True)\
                                             .distinct()
        total_ho_gia_dinh = ho_dang_sinh_song_ids.count()

        # Số hộ đã nộp trong đợt thu này
        ho_da_nop_ids = ChiTietThu.objects.filter(dot_thu=dot_thu, trang_thai_nop='Đã nộp')\
                                          .values_list('ho_gia_dinh_id', flat=True)\
                                          .distinct()

        # Đếm số hộ đã nộp mà vẫn đang sinh sống
        ho_gia_dinh_da_nop = len(set(ho_da_nop_ids).intersection(set(ho_dang_sinh_song_ids)))

        khoan_nop_info.append({
            'dot_thu': dot_thu,
            'ten_khoan_thu': dot_thu.khoan_thu.ten_khoan_thu,
            'so_luong_nop': f"{ho_gia_dinh_da_nop}/{total_ho_gia_dinh}",
            'thoi_gian': f"{dot_thu.thoi_gian_bat_dau} - {dot_thu.thoi_gian_ket_thuc}",
        })

    return render(request, 'thu_phi/view_list_khoannop.html', {
        'khoan_nop_info': khoan_nop_info,
        'query': query or ''
    })



@login_required
@role_required('Kế toán')
def khoannop_details(request, pk):
    dot_thu = get_object_or_404(DotThu, pk=pk)
    khoan_thu = dot_thu.khoan_thu

    if request.method == "POST" and request.headers.get("x-requested-with") == "XMLHttpRequest":
        ho_id = request.POST.get("ho_id")
        ho = get_object_or_404(HoGiaDinh, id=ho_id)

        new_date = request.POST.get("ngay_nop")
        new_so_tien = request.POST.get("so_tien_can_nop")

        chi_tiet = ChiTietThu.objects.filter(dot_thu=dot_thu, ho_gia_dinh=ho).first()

        if not chi_tiet:
            if new_so_tien is None:
                return JsonResponse({'success': False, 'error': 'Cần có số tiền khi tạo mới bản ghi.'})
            try:
                so_tien_int = int(new_so_tien)
            except ValueError:
                return JsonResponse({'success': False, 'error': 'Số tiền không hợp lệ.'})

            chi_tiet = ChiTietThu.objects.create(
                dot_thu=dot_thu,
                ho_gia_dinh=ho,
                so_tien_can_nop=so_tien_int,
                ngay_nop=parse_date(new_date) if new_date else None,
                trang_thai_nop="Đã nộp" if new_date else "Chưa nộp"
            )
        else:
            if new_so_tien is not None:
                try:
                    chi_tiet.so_tien_can_nop = int(new_so_tien)
                except ValueError:
                    return JsonResponse({'success': False, 'error': 'Số tiền không hợp lệ.'})

            if new_date is not None:
                chi_tiet.ngay_nop = parse_date(new_date) if new_date else None
                chi_tiet.trang_thai_nop = "Đã nộp" if chi_tiet.ngay_nop else "Chưa nộp"

            chi_tiet.save()

        return JsonResponse({'success': True})

    tat_ca_ho = HoGiaDinh.objects.select_related('id_chu_ho').prefetch_related('dancu_set').all()
    danh_sach_ho = []

    for ho in tat_ca_ho:
        chi_tiet = ChiTietThu.objects.filter(dot_thu=dot_thu, ho_gia_dinh=ho).first()
        so_tien = chi_tiet.so_tien_can_nop if chi_tiet else 0
        ngay_nop = chi_tiet.ngay_nop if chi_tiet else None
        so_nguoi = ho.dancu_set.count()

        danh_sach_ho.append({
            'ho_id': ho.id,
            'ten_chu_ho': ho.id_chu_ho.ho_ten,
            'so_can_ho': ho.so_can_ho,
            'dien_tich': ho.dien_tich,
            'so_nguoi': so_nguoi,
            'so_tien': so_tien,
            'ngay_nop': ngay_nop,
            'trang_thai_nop': "Đã nộp" if ngay_nop else "Chưa nộp",
        })

    return render(request, 'thu_phi/khoannop_details.html', {
        'dot_thu': dot_thu,
        'khoan_thu': khoan_thu,
        'danh_sach_ho': danh_sach_ho,
    })