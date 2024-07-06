from django.urls import path
from .views import VerifyPhoneNumberView

urlpatterns = [
    path('', VerifyPhoneNumberView.as_view(), name='Verify Phone Number'),
]