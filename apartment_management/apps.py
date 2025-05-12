from django.apps import AppConfig

class ApartmentManagementConfig(AppConfig):
    name = 'apartment_management'

    def ready(self):
        import apartment_management.signals
