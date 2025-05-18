from django.shortcuts import render
from ..models import TamTruTamVang

def danh_sach_tttv(request):
    danh_sach = TamTruTamVang.objects.select_related('dan_cu').all()
    return render(request, 'nhan_khau/tamtru_tamvang_list.html', {'danh_sach': danh_sach})
