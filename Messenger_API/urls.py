from django.urls import path
from .views import VerifyPhoneNumberView, UserProfileView, ChatView

urlpatterns = [
    path('', VerifyPhoneNumberView.as_view(), name='Verify Phone Number'),
    path('profile/', UserProfileView.as_view(), name='User Profile'),
    path('chat/<str:profile_id>/', ChatView.as_view(), name='Private Messaging'),
]