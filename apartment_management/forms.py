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
