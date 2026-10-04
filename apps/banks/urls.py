from django.urls import path

from .views import BankLoginView, BankRegisterView

urlpatterns = [
    path("register/", BankRegisterView.as_view(), name="bank-register"),
    path("login/", BankLoginView.as_view(), name="bank-login"),
]
