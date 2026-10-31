from django.urls import path
from .views import (
    AboutView,
    EthicsView,
    PrivacyPolicyView,
    TermsOfServiceView,
    ContactView,
)

app_name = 'core'

urlpatterns = [
    path('about/', AboutView.as_view(), name='about'),
    path('editorial-standards/', EthicsView.as_view(), name='ethics'),
    path('privacy-policy/', PrivacyPolicyView.as_view(), name='privacy'),
    path('terms-of-service/', TermsOfServiceView.as_view(), name='terms'),
    path('contact/', ContactView.as_view(), name='contact'),
]
