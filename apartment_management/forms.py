from django import forms
from .models import KhoanThu

# class KhoanThuForm(forms.ModelForm):
#     class Meta:
#         model = KhoanThu
#         fields = ['ten_khoan_thu', 'loai_khoan_thu', 'ghi_chu']
#         widgets = {
#             'ten_khoan_thu': forms.TextInput(attrs={'class': 'form-control', 'readonly': 'readonly'}),
#             'loai_khoan_thu': forms.Select(attrs={'class': 'form-control', 'disabled': 'disabled'}),
#             'ghi_chu': forms.Textarea(attrs={'class': 'form-control', 'readonly': 'readonly', 'rows': 10}),
#         }

class KhoanThuForm(forms.ModelForm):
    class Meta:
        model = KhoanThu
        fields = ['ten_khoan_thu', 'loai_khoan_thu', 'ghi_chu']
        widgets = {
            'ten_khoan_thu': forms.TextInput(attrs={'class': 'form-control', 'readonly': 'readonly'}),
            'loai_khoan_thu': forms.Select(attrs={
                'class': 'form-control readonly-select',  # Dùng class đặc biệt để khóa chọn
            }),
            'ghi_chu': forms.Textarea(attrs={'class': 'form-control', 'readonly': 'readonly', 'rows': 10}),
        }
