from django.db import models
from django.contrib.auth.models import User


class NguoiDung(models.Model):
    VAITRO_CHOICES = [
        ('Quản trị hệ thống', 'Quản trị hệ thống'),
        ('BQL Chung cư', 'BQL Chung cư'),
        ('Kế toán', 'Kế toán'),
    ]
    TRANGTHAI_CHOICES = [
        ('Đang hoạt động', 'Đang hoạt động'),
        ('Bị khóa', 'Bị khóa'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    vai_tro = models.CharField(max_length=50, choices=VAITRO_CHOICES)
    so_dien_thoai = models.CharField(max_length=20)
    trang_thai = models.CharField(max_length=20, choices=TRANGTHAI_CHOICES)

    def __str__(self):
        return self.user.username


class HoGiaDinh(models.Model):
    id_chu_ho = models.ForeignKey('DanCu', on_delete=models.PROTECT, related_name='chu_ho')
    so_can_ho = models.IntegerField()
    dien_tich = models.FloatField()
    ghi_chu = models.TextField(null=True, blank=True)
    thoi_gian_bat_dau_o = models.DateField()
    thoi_gian_ket_thuc_o = models.DateField(null=True, blank=True)
    TRANG_THAI_CHOICES = [
        ('Đang ở', 'Đang ở'),
        ('Đã rời đi', 'Đã rời đi'),
    ]
    trang_thai = models.CharField(max_length=20, choices=TRANG_THAI_CHOICES)

    def __str__(self):
        return f"Căn hộ {self.so_can_ho}"


class DanCu(models.Model):
    GIOI_TINH_CHOICES = [
        ('Nam', 'Nam'),
        ('Nữ', 'Nữ'),
    ]
    TRANG_THAI_CHOICES = [
        ('Đang sinh sống', 'Đang sinh sống'),
        ('Đã chuyển đi', 'Đã chuyển đi'),
        ('Đã qua đời', 'Đã qua đời'),
    ]

    ho_gia_dinh = models.ForeignKey(HoGiaDinh, on_delete=models.CASCADE)
    ho_ten = models.CharField(max_length=100)
    ngay_sinh = models.DateField()
    gioi_tinh = models.CharField(max_length=5, choices=GIOI_TINH_CHOICES)
    ma_can_cuoc = models.CharField(max_length=15)
    so_dien_thoai = models.CharField(max_length=15)
    trang_thai = models.CharField(max_length=20, choices=TRANG_THAI_CHOICES)
    thoi_gian_chuyen_den = models.DateField()
    thoi_gian_chuyen_di = models.DateField(null=True, blank=True)

    def __str__(self):
        return self.ho_ten


class KhoanThu(models.Model):
    LOAI_CHOICES = [
        ('Bắt buộc', 'Bắt buộc'),
        ('Tự nguyện', 'Tự nguyện'),
    ]
    ten_khoan_thu = models.CharField(max_length=100)
    loai_khoan_thu = models.CharField(max_length=20, choices=LOAI_CHOICES)
    so_tien = models.FloatField(default=0)
    ghi_chu = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.ten_khoan_thu


class DotThu(models.Model):
    TRANG_THAI_CHOICES = [
        ('Đã hoàn thành', 'Đã hoàn thành'),
        ('Đang tiến hành', 'Đang tiến hành'),
        ('Chưa bắt đầu', 'Chưa bắt đầu'),
    ]
    khoan_thu = models.ForeignKey(KhoanThu, on_delete=models.CASCADE)
    ten_dot_thu = models.CharField(max_length=150)
    noi_dung = models.TextField(null=True, blank=True)
    thoi_gian_bat_dau = models.DateField()
    thoi_gian_ket_thuc = models.DateField()
    trang_thai = models.CharField(max_length=20, choices=TRANG_THAI_CHOICES)

    def __str__(self):
        return self.ten_dot_thu


class ChiTietThu(models.Model):
    dot_thu = models.ForeignKey(DotThu, on_delete=models.CASCADE)
    ho_gia_dinh = models.ForeignKey(HoGiaDinh, on_delete=models.CASCADE)
    so_tien_can_nop = models.FloatField()
    TRANG_THAI_NOP_CHOICES = [
        ('Đã nộp', 'Đã nộp'),
        ('chưa nộp', 'chưa nộp'),
    ]
    trang_thai_nop = models.CharField(max_length=20, choices=TRANG_THAI_NOP_CHOICES)
    ngay_nop = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.ho_gia_dinh} - {self.dot_thu}"


class TamTruTamVang(models.Model):
    LOAI_CHOICES = [
        ('Tạm trú', 'Tạm trú'),
        ('Tạm vắng', 'Tạm vắng'),
    ]
    dan_cu = models.ForeignKey(DanCu, on_delete=models.CASCADE)
    loai_tttv = models.CharField(max_length=20, choices=LOAI_CHOICES)
    thoi_gian_bat_dau = models.TimeField()
    thoi_gian_ket_thuc = models.TimeField()
    ly_do = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.dan_cu} - {self.loai_tttv}"


class PhuongTien(models.Model):
    LOAI_CHOICES = [
        ('Ô tô', 'Ô tô'),
        ('Xe máy', 'Xe máy'),
        ('Xe đạp', 'Xe đạp'),
    ]
    ho_gia_dinh = models.ForeignKey(HoGiaDinh, on_delete=models.CASCADE)
    loai_phuong_tien = models.CharField(max_length=20, choices=LOAI_CHOICES)
    bien_so = models.CharField(max_length=255)
    mau = models.CharField(max_length=255)
    mo_ta = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.bien_so
