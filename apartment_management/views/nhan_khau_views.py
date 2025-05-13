# apartment_management/views/nhan_khau_views.py
from django.shortcuts import render, redirect
from apartment_management.models import DanCu  # Nhập model DanCu để lưu dữ liệu vào database
from django.http import HttpResponse
def resident_list(request):
    # Lấy tất cả nhân khẩu từ cơ sở dữ liệu
    residents = DanCu.objects.all()
    # Trả về template với danh sách nhân khẩu
    return render(request, 'nhan_khau/residents.html', {'residents': residents})
def add_resident(request):
    if request.method == 'POST':
        # Lấy input
        so_can_ho = request.POST.get('so_can_ho')
        # Tìm hoặc tạo
        hogiadinh, _ = HoGiaDinh.objects.get_or_create(
            so_can_ho=so_can_ho,
            defaults={
              'dien_tich':0.0,
              'ghi_chu':'',
              'thoi_gian_bat_dau_o': request.POST['thoi_gian_chuyen_den'],
              'trang_thai':'Đang ở'
            }
        )

        # Lấy các field khác
        ho_ten    = request.POST['ho_ten']
        ngay_sinh = request.POST['ngay_sinh']
        gioi_tinh = request.POST['gioi_tinh']
        ma_cccd   = request.POST['cccd']
        sdt       = request.POST.get('so_dien_thoai','')
        t_den     = request.POST['thoi_gian_chuyen_den']

        # Tạo DanCu
        DanCu.objects.create(
          ho_gia_dinh=hogiadinh,
          ho_ten=ho_ten,
          ngay_sinh=ngay_sinh,
          gioi_tinh=gioi_tinh,
          ma_can_cuoc=ma_cccd,
          so_dien_thoai=sdt,
          thoi_gian_chuyen_den=t_den,
          trang_thai='Đang sinh sống'
        )
        return redirect('resident_list')

    return render(request, 'nhan_khau/add_resident.html')