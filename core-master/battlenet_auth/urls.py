from django.conf import settings
from django.urls import path
from social_core.utils import setting_name

from .views import IndexView, LoginView, CompleteView

extra = getattr(settings, setting_name('TRAILING_SLASH'), True) and '/' or ''

app_name = 'social_battlenet'

urlpatterns = [
    path(r'battlenet/auth/', IndexView.as_view(), name='index'),
    path(r'battlenet/login/', LoginView.as_view(), name='begin'),
    path(r'battlenet/complete/', CompleteView.as_view(), name='complete'),
]
