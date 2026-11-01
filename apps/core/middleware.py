from django.conf import settings
from apps.core.models import CustomUser

class DevAdminAutoLoginMiddleware:
    """
    Development-only middleware for capturing screenshots and local previews of Unfold Admin.
    Defense-in-depth: Immediately no-ops if settings.DEBUG is False.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not getattr(settings, 'DEBUG', False):
            return self.get_response(request)

        if request.path.startswith('/admin/'):
            admin_user = CustomUser.objects.filter(is_superuser=True).first()
            if admin_user:
                request.user = admin_user
        return self.get_response(request)
