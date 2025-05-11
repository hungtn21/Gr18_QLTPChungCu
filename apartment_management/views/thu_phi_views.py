
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .nguoi_dung_views import role_required
from ..models import KhoanThu
from django.db.models import Q
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from ..forms import KhoanThuForm

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