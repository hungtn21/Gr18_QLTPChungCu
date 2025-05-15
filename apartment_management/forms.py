from django import forms
from .models import ChiTietThu, DanCu, HoGiaDinh, KhoanThu


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
        fields = ['ho_ten', 'ma_can_cuoc', 'ngay_sinh', 'gioi_tinh', 'trang_thai']
        widgets = {
            'ho_ten': forms.TextInput(attrs={'class': 'form-control'}),
            'ma_can_cuoc': forms.TextInput(attrs={'class': 'form-control'}),
            'ngay_sinh': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'gioi_tinh': forms.Select(attrs={'class': 'form-control'}),
            'trang_thai': forms.Select(attrs={'class': 'form-control'}),
        }


class HoGiaDinhForm(forms.ModelForm):
    class Meta:
        model = HoGiaDinh
        fields = [
            'id_chu_ho',
            'so_can_ho',
            'dien_tich',
            'ghi_chu',
            'thoi_gian_bat_dau_o',
            'trang_thai',
        ]
        widgets = {
            'id_chu_ho': forms.Select(attrs={'class': 'form-control'}),
            'so_can_ho': forms.NumberInput(attrs={'class': 'form-control'}),
            'dien_tich': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1'}),
            'ghi_chu': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'thoi_gian_bat_dau_o': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'trang_thai': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)  # ✅ dùng super() kiểu mới trong Python 3
        self.fields['id_chu_ho'].queryset = DanCu.objects.filter(trang_thai='Đang sinh sống')
        self.fields['id_chu_ho'].label = "Chủ hộ"
        self.fields['thoi_gian_bat_dau_o'].label = "Ngày bắt đầu ở"
