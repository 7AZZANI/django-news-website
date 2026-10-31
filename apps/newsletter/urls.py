from django.urls import path
from .views import SubscribeView, UnsubscribeView

app_name = 'newsletter'

urlpatterns = [
    path('subscribe/', SubscribeView.as_view(), name='subscribe'),
    path('unsubscribe/<uuid:token>/', UnsubscribeView.as_view(), name='unsubscribe'),
]
