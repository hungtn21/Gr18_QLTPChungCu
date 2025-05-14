from django.contrib import admin
from .models import NguoiDung
# Register your models here.

@admin.register(NguoiDung)
class NguoiDungAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'vai_tro', 'trang_thai')