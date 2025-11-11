# users/mobile_urls.py
from django.urls import path
from .mobile_auth import PublicRegisterView

urlpatterns = [
    path('auth/public-register/', PublicRegisterView.as_view(), name='public_register'),
]
