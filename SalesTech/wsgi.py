import os

from django.core.wsgi import get_wsgi_application

from dashboard.utils import init_app_settings
from users.utils import create_rate_plans, init_groups
from crm.utils import init_currencies

init_app_settings()
init_currencies()
init_groups()
create_rate_plans()

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'SalesTech.settings')

application = get_wsgi_application()
