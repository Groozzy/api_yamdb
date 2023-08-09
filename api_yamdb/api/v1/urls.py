from django.urls import path

from .views import SignupView

urlpatterns = [
    path('auth/signup/', SignupView),
]
