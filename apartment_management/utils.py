from collections import defaultdict
from apartment_management.models import ChiTietThu
from .models import ChiTietThu
from django.db import transaction

def xoa_chi_tiet_thu_trung_lap():
    duplicates = defaultdict(list)

    # Gom nhóm theo (dot_thu_id, ho_gia_dinh_id)
    for ct in ChiTietThu.objects.all():
        key = (ct.dot_thu_id, ct.ho_gia_dinh_id)
        duplicates[key].append(ct)

    count_deleted = 0
    for key, records in duplicates.items():
        if len(records) > 1:
            # Giữ lại 1 bản ghi đầu tiên, xóa các bản ghi còn lại
            for ct in records[1:]:
                ct.delete()
                count_deleted += 1

    print(f"Đã xóa {count_deleted} bản ghi ChiTietThu bị trùng lặp.")


# apartment_management/utils.py


def xoa_tat_ca_chi_tiet_thu():
    """
    Function để xóa toàn bộ dữ liệu trong bảng ChiTietThu.
    """
    try:
        with transaction.atomic():
            # Xóa tất cả các bản ghi trong bảng ChiTietThu
            ChiTietThu.objects.all().delete()
            print("Đã xóa toàn bộ dữ liệu trong bảng ChiTietThu.")
    except Exception as e:
        print(f"Lỗi khi xóa dữ liệu: {e}")