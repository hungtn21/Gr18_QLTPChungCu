from django import forms
from .models import ChiTietThu, DanCu, HoGiaDinh, KhoanThu, NguoiDung
from django.core.validators import RegexValidator



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
