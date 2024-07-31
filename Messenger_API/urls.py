from django.urls import path
from .views import ChatView

urlpatterns = [
    path('chat/<str:profile_id>/', ChatView.as_view(), name='Private Messaging'),
]