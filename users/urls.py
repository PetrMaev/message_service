from django.urls import path

from users.apps import UsersConfig
from users.views import (ConfirmRegisterView, CustomLoginView, CustomLogoutView, RegisterView, UserDetailVew,
                         UserForgotPasswordView, UserListView, UserPasswordChangeView, UserPasswordResetConfirmView,
                         UserUpdateView, email_verification)

app_name = UsersConfig.name

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", CustomLoginView.as_view(), name="login"),
    path("logout/", CustomLogoutView.as_view(), name="logout"),
    path("user_detail/<int:pk>/", UserDetailVew.as_view(), name="user_detail"),
    path("user_list/", UserListView.as_view(), name="user_list"),
    path("edit/<int:pk>/", UserUpdateView.as_view(), name="user_edit"),
    path("email-confirm/<str:token>/", email_verification, name="email-confirm"),
    path("users/confirm_register/", ConfirmRegisterView.as_view(), name="confirm_register"),
    path("password-change/", UserPasswordChangeView.as_view(), name="password_change"),
    path("password-reset/", UserForgotPasswordView.as_view(), name="password_reset"),
    path("set-new-password/<uidb64>/<token>/", UserPasswordResetConfirmView.as_view(), name="password_reset_confirm"),
]
