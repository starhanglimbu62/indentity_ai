from django.urls import path

from .views import BankLoginView, BankRegisterView, BankGetInfoView

urlpatterns = [
    path("register/", BankRegisterView.as_view(), name="bank-register"),
    path("login/", BankLoginView.as_view(), name="bank-login"),
    path("info/", BankGetInfoView.as_view(), name="bank-info"),
]
