from django.conf.urls.i18n import i18n_patterns
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from django.views.i18n import JavaScriptCatalog
from django.views.generic.base import RedirectView

from ratelimit.exceptions import Ratelimited

from SalesTech import settings
from users.views import blocked_register, blocked_forgotpassword, custom_forbidden_view
from users.views import blocked_user_login

urlpatterns = [
    path('i18n/', include('django.conf.urls.i18n')),
    path('', include('django_prometheus.urls')),
    path('', RedirectView.as_view(pattern_name='home', permanent=False)),
]

urlpatterns += i18n_patterns(
    path('jsi18n/', JavaScriptCatalog.as_view(), name='javascript-catalog'),
    path('captcha/', include('captcha.urls')),
    path('company/', include("company.urls")),
    path('admin/', admin.site.urls),
    path('refs/', include("refferal.urls")),
    path('users/', include("users.urls")),
    path('crm/', include("crm.urls")),
    path('', include("dashboard.urls")),

    path('notifications/', include('django_nyt.urls')),
    path('wiki/', include("wiki.urls"), name='wiki_lib'),
    path('pay/', include('payment.urls')),
)

urlpatterns += static('/media', document_root=settings.MEDIA_ROOT)


def handler403(request, exception=None):
    if isinstance(exception, Ratelimited):
        if '/register/' in request.path:
            return blocked_register(request, exception)
        elif '/login/' in request.path:
            return blocked_user_login(request, exception)
        elif 'forgot/' in request.path:
            return blocked_forgotpassword(request, exception)
    return custom_forbidden_view(request, exception)


handler404 = 'users.views.custom_page_not_found_view'
handler500 = 'users.views.custom_server_error_view'
