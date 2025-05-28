from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404, redirect
from apartment_management.models import DotThu, ChiTietThu, KhoanThu, DanCu, NguoiDung
from datetime import datetime
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.utils.dateparse import parse_date
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.db import transaction
from django.contrib import messages
from apartment_management.forms import EditProfileForm  # Import the EditProfileForm


# ================== API lấy danh sách khoản thu cho autocomplete ==================
def api_khoan_thu_list(request):
    khoan_thu_list = KhoanThu.objects.values_list('ten_khoan_thu', flat=True)
    return JsonResponse(list(khoan_thu_list), safe=False)


# ================== View danh sách đợt thu ==================
def list_dot_thu_view(request):
    try:
        page = int(request.GET.get('page', 1))
    except ValueError:
        page = 1

    try:
        per_page = int(request.GET.get('per_page', 10))
    except ValueError:
        per_page = 10

    # Tìm kiếm
    search_ten = request.GET.get('ten_dot_thu', '').strip()
    search_khoan = request.GET.get('khoan_thu', '').strip()
    search_trang_thai = request.GET.get('trang_thai', '').strip()
    start_date = request.GET.get('start_date', '').strip()
    end_date = request.GET.get('end_date', '').strip()

    dot_thu_list = DotThu.objects.select_related('khoan_thu').all()

    today = datetime.now().date()

    if search_ten:
        dot_thu_list = dot_thu_list.filter(ten_dot_thu__icontains=search_ten)
    if search_khoan:
        dot_thu_list = dot_thu_list.filter(khoan_thu__ten_khoan_thu__icontains=search_khoan)
    if search_trang_thai:
        dot_thu_list = dot_thu_list.filter(trang_thai__icontains=search_trang_thai)
    if start_date:
        try:
            start_dt = datetime.strptime(start_date, '%Y-%m-%d').date()
            dot_thu_list = dot_thu_list.filter(thoi_gian_bat_dau__gte=start_dt)
        except ValueError:
            pass
    if end_date:
        try:
            end_dt = datetime.strptime(end_date, '%Y-%m-%d').date()
            dot_thu_list = dot_thu_list.filter(thoi_gian_ket_thuc__lte=end_dt)
        except ValueError:
            pass
    to_update = []
    for dot in dot_thu_list:
        if dot.thoi_gian_ket_thuc < today and dot.trang_thai != "Đã kết thúc":
            dot.trang_thai = "Đã kết thúc"
            to_update.append(dot)
        elif dot.thoi_gian_bat_dau <= today <= dot.thoi_gian_ket_thuc and dot.trang_thai != "Đang tiến hành":
            dot.trang_thai = "Đang tiến hành"
            to_update.append(dot)

    if to_update:
        DotThu.objects.bulk_update(to_update, ['trang_thai'])
    # Phân trang
    paginator = Paginator(dot_thu_list, per_page)
    page_obj = paginator.get_page(page)
    total_pages = paginator.num_pages
    current_page = page_obj.number
    page_start_index = (current_page - 1) * per_page + 1
    if total_pages <= 5:
        start_page = 1
        end_page = total_pages
    elif current_page <= 3:
        start_page = 1
        end_page = 5
    elif current_page >= total_pages - 2:
        start_page = total_pages - 4
        end_page = total_pages
    else:
        start_page = current_page - 2
        end_page = current_page + 2

    start_page = max(start_page, 1)
    danh_sach_khoan_thu = KhoanThu.objects.all()
    context = {
        'dot_thu_list': page_obj.object_list,
        'page_obj': page_obj,
        'paginator': paginator,
        'per_page': per_page,
        'total_count': paginator.count,
        'start_page': start_page,
        'end_page': end_page,
        'search_ten': search_ten,
        'search_khoan': search_khoan,
        'search_trang_thai': search_trang_thai,
        'start_date': start_date,
        'end_date': end_date,
        'page_start_index': page_start_index,
        'danh_sach_khoan_thu': danh_sach_khoan_thu,
    }

    return render(request, 'thu_phi/list_dot_thu.html', context)


# ================== View chi tiết đợt thu ==================
def chi_tiet_dot_thu_view(request, dot_id):
    dot_thu = get_object_or_404(DotThu.objects.select_related('khoan_thu'), id=dot_id)
    khoan_thu = dot_thu.khoan_thu

    chi_tiet = ChiTietThu.objects.filter(dot_thu=dot_thu)
    tong_da_nop = sum(ctt.so_tien_can_nop for ctt in chi_tiet if ctt.trang_thai_nop == 'Đã nộp')
    ho_da_nop = sum(1 for ctt in chi_tiet if ctt.trang_thai_nop == 'Đã nộp')

    return render(request, 'thu_phi/detail_dot_thu.html', {
        'dot_thu': dot_thu,
        'khoan_thu': khoan_thu,
        'ho_da_nop': ho_da_nop,
        'tong_da_nop': tong_da_nop,
    })


# ================== View sửa đợt thu ==================
@require_POST
@csrf_exempt
def sua_dot_thu_view(request, dot_id):
    try:
        dot_thu = get_object_or_404(DotThu, id=dot_id)

        data = {
            'ten_dot_thu': request.POST.get('ten_dot_thu', '').strip(),
            'noi_dung': request.POST.get('noi_dung', '').strip(),
            'thoi_gian_bat_dau': request.POST.get('thoi_gian_bat_dau', '').strip(),
            'thoi_gian_ket_thuc': request.POST.get('thoi_gian_ket_thuc', '').strip(),
        }

        # Kiểm tra bắt buộc
        for field in data:
            if not data[field]:
                return JsonResponse({'success': False, 'error': f'Trường {field} là bắt buộc'})

        # Kiểm tra ngày tháng
        try:
            ngay_bat_dau = parse_date(data['thoi_gian_bat_dau'])
            ngay_ket_thuc = parse_date(data['thoi_gian_ket_thuc'])
            if not ngay_bat_dau or not ngay_ket_thuc:
                raise ValueError
            if ngay_bat_dau > ngay_ket_thuc:
                return JsonResponse({'success': False, 'error': 'Ngày kết thúc phải sau ngày bắt đầu'})
        except Exception:
            return JsonResponse({'success': False, 'error': 'Ngày tháng không hợp lệ'})

        # Cập nhật đợt thu
        with transaction.atomic():
            dot_thu.ten_dot_thu = data['ten_dot_thu']
            dot_thu.noi_dung = data['noi_dung']
            dot_thu.thoi_gian_bat_dau = ngay_bat_dau
            dot_thu.thoi_gian_ket_thuc = ngay_ket_thuc
            dot_thu.save()

        return JsonResponse({'success': True})

    except Exception as e:
        return JsonResponse({'success': False, 'error': f'Lỗi hệ thống: {str(e)}'})

# ================== View xoá đợt thu ==================
@require_POST
@csrf_exempt
def xoa_dot_thu_view(request, dot_id):
    try:
        dot_thu = get_object_or_404(DotThu, id=dot_id)

        # Nếu đã có người nộp => không được xoá
        if ChiTietThu.objects.filter(dot_thu=dot_thu, trang_thai_nop='Đã nộp').exists():
            return JsonResponse({
                'success': False,
                'error': 'Đợt thu này đã có hộ nộp tiền, không thể xóa'
            })

        with transaction.atomic():
            ChiTietThu.objects.filter(dot_thu=dot_thu).delete()
            dot_thu.delete()

        return JsonResponse({'success': True})

    except DotThu.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Đợt thu không tồn tại'})

    except Exception as e:
        return JsonResponse({'success': False, 'error': f'Lỗi hệ thống: {str(e)}'})

# ================== View tạo đợt thu ==================
@require_POST
@csrf_exempt
def tao_dot_thu_view(request):
    try:
        data = {
            'ten_dot_thu': request.POST.get('ten_dot_thu', '').strip(),
            'noi_dung': request.POST.get('noi_dung', '').strip(),
            'thoi_gian_bat_dau': request.POST.get('thoi_gian_bat_dau', '').strip(),
            'thoi_gian_ket_thuc': request.POST.get('thoi_gian_ket_thuc', '').strip(),
            'ten_khoan_thu': request.POST.get('ten_khoan_thu', '').strip(),
        }

        for key in data:
            if not data[key]:
                return JsonResponse({'success': False, 'error': f'Trường {key} là bắt buộc'})

        start = parse_date(data['thoi_gian_bat_dau'])
        end = parse_date(data['thoi_gian_ket_thuc'])
        if not start or not end:
            return JsonResponse({'success': False, 'error': 'Ngày không hợp lệ'})
        if start > end:
            return JsonResponse({'success': False, 'error': 'Thời gian bắt đầu phải trước thời gian kết thúc'})

        khoan = KhoanThu.objects.filter(ten_khoan_thu=data['ten_khoan_thu']).first()
        if not khoan:
            return JsonResponse({'success': False, 'error': 'Khoản thu không tồn tại'})

        now = datetime.now().date()
        if start <= now <= end:
            trang_thai = "Đang tiến hành"
        elif now < start:
            trang_thai = "Chưa bắt đầu"
        else:
            trang_thai = "Đã kết thúc"

        DotThu.objects.create(
            ten_dot_thu=data['ten_dot_thu'],
            noi_dung=data['noi_dung'],
            thoi_gian_bat_dau=start,
            thoi_gian_ket_thuc=end,
            khoan_thu=khoan,
            trang_thai=trang_thai
        )

        return JsonResponse({'success': True})

    except Exception as e:
        return JsonResponse({'success': False, 'error': f'Lỗi hệ thống: {str(e)}'})
 
    
#---------------------------------Đổi mật khẩu----------------------------------------
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

    return render(request, 'thu_phi/change_password.html', {'form': form})

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
            return redirect('edit_profile')
    else:
        form = EditProfileForm(instance=nguoi_dung)

    return render(request, 'thu_phi/edit_profile.html', {'form': form})

@login_required
def logout_view(request):
    logout(request)
    return redirect('login')  # 'login' là tên URL pattern cho trang đăng nhập