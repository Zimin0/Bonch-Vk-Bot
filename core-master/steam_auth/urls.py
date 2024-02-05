from django.conf import settings
from django.urls import path
from social_core.utils import setting_name

from . import views
from .views import IndexView

extra = getattr(settings, setting_name('TRAILING_SLASH'), True) and '/' or ''

app_name = 'social_steam'

urlpatterns = [
    path(r'steam/auth/', IndexView.as_view(), name='index'),
    path(f'login/<str:backend>', views.auth,
         name='begin'),
    path(f'complete/<str:backend>{extra}', views.complete,
         name='complete'),
]
