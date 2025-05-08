from django.apps import AppConfig
import logging

logger = logging.getLogger(__name__)

class ApartmentManagementConfig(AppConfig):
    name = 'apartment_management'

    def ready(self):
        try:
            from decouple import config
            from django.contrib.auth.models import User
            from .models import NguoiDung

            accounts = [
                 {
                    "username": config("ADMIN_USERNAME"),
                    "email": config("ADMIN_EMAIL"),
                    "password": config("ADMIN_PASSWORD"),
                    "phone": config("ADMIN_PHONE"),
                    "role": config("ADMIN_ROLE"),
                },
                {
                    "username": config("BQL_USERNAME"),
                    "email": config("BQL_EMAIL"),
                    "password": config("BQL_PASSWORD"),
                    "phone": config("BQL_PHONE"),
                    "role": config("BQL_ROLE"),
                },
                {
                    "username": config("KT_USERNAME"),
                    "email": config("KT_EMAIL"),
                    "password": config("KT_PASSWORD"),
                    "phone": config("KT_PHONE"),
                    "role": config("KT_ROLE"),
                },
            ]

            for acc in accounts:
                if not User.objects.filter(username=acc["username"]).exists():
                    user = User.objects.create_user(
                        username=acc["username"],
                        email=acc["email"],
                        password=acc["password"]
                    )
                    NguoiDung.objects.create(
                        user=user,
                        vai_tro=acc["role"],
                        so_dien_thoai=acc["phone"],
                        trang_thai="Đang hoạt động"
                    )
                    logger.info(f" Tạo tài khoản: {acc['username']}")
        except Exception as e:
            logger.warning(f" Không thể tạo tài khoản mẫu: {e}")
