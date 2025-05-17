from django import forms
from datetime import date
from .models import ChiTietThu, DanCu, HoGiaDinh, KhoanThu
from .models import KhoanThu
from .models import NguoiDung
from django.core.validators import RegexValidator
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
class EditProfileForm(forms.ModelForm):
    ho_ten = forms.CharField(label='Họ và tên', required=True)
    email = forms.EmailField(label='Email', required=True)
    so_dien_thoai = forms.CharField(
        label='Số điện thoại',
        validators=[
            RegexValidator(
                regex='^[0-9]*$',
                message='Số điện thoại chỉ được chứa chữ số',
                code='invalid_phone'
            )
        ]
    )

    class Meta:
        model = NguoiDung
        fields = ['so_dien_thoai']  # Chỉ giữ lại số điện thoại
        labels = {
            'so_dien_thoai': 'Số điện thoại'
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and hasattr(self.instance, 'user'):
            self.fields['ho_ten'].initial = f"{self.instance.user.last_name} {self.instance.user.first_name}"
            self.fields['email'].initial = self.instance.user.email
            self.fields['so_dien_thoai'].initial = self.instance.so_dien_thoai

# class KhoanThuForm(forms.ModelForm):
#     class Meta:
#         model = KhoanThu
#         fields = ['ten_khoan_thu', 'loai_khoan_thu', 'ghi_chu']
#         widgets = {
#             'ten_khoan_thu': forms.TextInput(attrs={'class': 'form-control', 'readonly': 'readonly'}),
#             'loai_khoan_thu': forms.Select(attrs={
#                 'class': 'form-control readonly-select',
#             }),
#             'ghi_chu': forms.Textarea(attrs={'class': 'form-control', 'readonly': 'readonly', 'rows': 10}),
#         }


# class KhoanThuCreateForm(forms.ModelForm):
#     class Meta:
#         model = KhoanThu
#         fields = ['ten_khoan_thu', 'loai_khoan_thu', 'ghi_chu']
#         widgets = {
#             'ten_khoan_thu': forms.TextInput(attrs={'class': 'form-control'}),
#             'loai_khoan_thu': forms.Select(attrs={'class': 'form-control'}),
#             'ghi_chu': forms.Textarea(attrs={'class': 'form-control', 'rows': 10}),
#         }

class KhoanThuForm(forms.ModelForm):
    class Meta:
        model = KhoanThu
        fields = ['ten_khoan_thu', 'loai_khoan_thu', 'so_tien', 'ghi_chu']
        widgets = {
            'ten_khoan_thu': forms.TextInput(attrs={'class': 'form-control', 'readonly': 'readonly'}),
            'loai_khoan_thu': forms.Select(attrs={'class': 'form-control readonly-select'}),
            'so_tien': forms.NumberInput(attrs={'class': 'form-control', 'readonly': 'readonly'}),
            'ghi_chu': forms.Textarea(attrs={'class': 'form-control', 'readonly': 'readonly', 'rows': 10}),
        }

class KhoanThuCreateForm(forms.ModelForm):
    class Meta:
        model = KhoanThu
        fields = ['ten_khoan_thu', 'loai_khoan_thu', 'so_tien', 'ghi_chu']
        widgets = {
            'ten_khoan_thu': forms.TextInput(attrs={'class': 'form-control'}),
            'loai_khoan_thu': forms.Select(attrs={'class': 'form-control'}),
            'so_tien': forms.NumberInput(attrs={'class': 'form-control'}),
            'ghi_chu': forms.Textarea(attrs={'class': 'form-control', 'rows': 10}),
        }


class KhoanNopCreateForm(forms.ModelForm):
    ho_gia_dinh = forms.ModelChoiceField(queryset=HoGiaDinh.objects.all(), label="Chọn căn hộ", empty_label="-- Chọn căn hộ --")
    so_tien_can_nop = forms.FloatField(label="Số tiền cần nộp", min_value=0)

    class Meta:
        model = ChiTietThu
        fields = ['ho_gia_dinh', 'so_tien_can_nop']

class DanCuForm(forms.ModelForm):
    class Meta:
        model = DanCu
        fields = [
            'ho_ten',
            'ngay_sinh',
            'gioi_tinh',
            'ma_can_cuoc',
            'so_dien_thoai',
            'trang_thai',
            'thoi_gian_chuyen_den',
            'thoi_gian_chuyen_di'
        ]
        widgets = {
            'ngay_sinh': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'thoi_gian_chuyen_den': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'thoi_gian_chuyen_di': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'gioi_tinh': forms.Select(attrs={'class': 'form-select'}),
            'trang_thai': forms.Select(attrs={'class': 'form-select'}),
        }
    def clean_ma_can_cuoc(self):
        cccd = self.cleaned_data.get('ma_can_cuoc')
        if not cccd.isdigit() or len(cccd) != 12:
            raise forms.ValidationError("CCCD phải có đúng 12 chữ số.")
        return cccd

    def clean_so_dien_thoai(self):
        sdt = self.cleaned_data.get('so_dien_thoai')
        if not sdt.isdigit() or len(sdt) != 10:
            raise forms.ValidationError("Số điện thoại phải có đúng 10 chữ số.")
        return sdt

    def clean_ngay_sinh(self):
        ns = self.cleaned_data.get('ngay_sinh')
        if ns > date.today():
            raise forms.ValidationError("Ngày sinh không được lớn hơn hiện tại.")
        return ns

    def clean(self):
        cleaned = super().clean()
        chuyen_den = cleaned.get('thoi_gian_chuyen_den')
        chuyen_di = cleaned.get('thoi_gian_chuyen_di')

        if chuyen_den is None:
            self.add_error('thoi_gian_chuyen_den', 'Không được để trống')

        if chuyen_den and chuyen_di and chuyen_di < chuyen_den:
            self.add_error('thoi_gian_chuyen_di', 'Phải sau ngày chuyển đến')
        return cleaned



class HoGiaDinhForm(forms.ModelForm):
    class Meta:
        model = HoGiaDinh
        fields = [
            'so_can_ho',
            'dien_tich',
            'ghi_chu',
            'thoi_gian_bat_dau_o',
            'trang_thai',
        ]
        widgets = {
            'so_can_ho': forms.NumberInput(attrs={'class': 'form-control'}),
            'dien_tich': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1'}),
            'ghi_chu': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'thoi_gian_bat_dau_o': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'trang_thai': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['thoi_gian_bat_dau_o'].label = "Ngày bắt đầu ở"

    def clean_so_can_ho(self):
        so_can_ho = self.cleaned_data['so_can_ho']
        # Kiểm tra trùng số căn hộ khi tạo mới hoặc khi sửa đổi số căn hộ
        if not self.instance.pk or self.instance.so_can_ho != so_can_ho:
            if HoGiaDinh.objects.filter(so_can_ho=so_can_ho).exists():
                raise ValidationError("Số căn hộ này đã tồn tại.")
        return so_can_ho