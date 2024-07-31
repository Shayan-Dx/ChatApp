from django.urls import path
from .views import VerifyPhoneNumberView, UserProfileView, UserSearchView


urlpatterns = [
    path('', VerifyPhoneNumberView.as_view(), name='Verify Phone Number'),
    path('profile/', UserProfileView.as_view(), name='User Profile'),
    path('search/', UserSearchView.as_view(), name='search-phones'),
]