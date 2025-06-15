import secrets

from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.auth.views import (LoginView, LogoutView, PasswordChangeView, PasswordResetConfirmView,
                                       PasswordResetView)
from django.contrib.messages.views import SuccessMessageMixin
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import DetailView, ListView, TemplateView
from django.views.generic.edit import CreateView, UpdateView

from config.settings import EMAIL_HOST_USER
from users.forms import (CustomUserCreationForm, CustomUserUpdateForm, UserForgotPasswordForm, UserPasswordChangeForm,
                         UserSetNewPasswordForm)
from users.models import CustomUser


class ConfirmRegisterView(TemplateView):
    model = CustomUser
    template_name = "users/confirm_register.html"
    context_object_name = "user"


class RegisterView(CreateView):
    template_name = "users/register.html"
    form_class = CustomUserCreationForm
    success_url = reverse_lazy("users:confirm_register")

    def form_valid(self, form):
        user = form.save()
        user.is_active = False
        token = secrets.token_hex(16)
        user.token = token
        user.save()
        host = self.request.get_host()
        url = f"http://{host}/users/email-confirm/{token}/"
        send_mail(
            subject="Подтверждение почты",
            message=f"Привет! Перейди по ссылке для подтверждения почты {url}",
            from_email=EMAIL_HOST_USER,
            recipient_list=[
                user.email,
            ],
        )
        return super().form_valid(form)


def email_verification(request, token):
    user = get_object_or_404(CustomUser, token=token)
    user.is_active = True
    user.save()
    return redirect(reverse("users:login"))


class CustomLoginView(LoginView):
    template_name = "users/login.html"
    next_page = reverse_lazy("mailing_service:home")


class CustomLogoutView(LogoutView):
    def get_next_page(self):
        return reverse_lazy("mailing_service:home")


class UserDetailVew(DetailView):
    model = CustomUser
    template_name = "users/user_detail.html"
    context_object_name = "user"


class UserUpdateView(UpdateView):
    model = CustomUser
    form_class = CustomUserUpdateForm
    template_name = "users/user_edit.html"

    def get_success_url(self):
        return reverse("users:user_detail", kwargs={"pk": self.object.pk})


class UserListView(PermissionRequiredMixin, ListView):
    permission_required = "users.can_view_list_user"
    model = CustomUser
    template_name = "users/user_list.html"
    context_object_name = "users"


class UserPasswordChangeView(SuccessMessageMixin, PasswordChangeView):
    """
    Изменение пароля пользователя
    """

    form_class = UserPasswordChangeForm
    template_name = "users/user_password_change.html"
    success_message = "Ваш пароль был успешно изменён!"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Изменение пароля на сайте"
        return context

    def get_success_url(self):
        return reverse_lazy("users:user_detail", kwargs={"pk": self.request.user.pk})


class UserForgotPasswordView(SuccessMessageMixin, PasswordResetView):
    """
    Представление по сбросу пароля по почте
    """

    form_class = UserForgotPasswordForm
    template_name = "users/user_password_reset.html"
    success_url = reverse_lazy("mailing_service:home")
    success_message = "Письмо с инструкцией по восстановлению пароля отправлено на ваш email"
    subject_template_name = "users/email/password_subject_reset_mail.txt"
    email_template_name = "users/email/password_reset_mail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Запрос на восстановление пароля"
        return context


class UserPasswordResetConfirmView(SuccessMessageMixin, PasswordResetConfirmView):
    """
    Представление установки нового пароля
    """

    form_class = UserSetNewPasswordForm
    template_name = "users/user_password_set_new.html"
    success_url = reverse_lazy("mailing_service:home")
    success_message = "Пароль успешно изменен. Можете авторизоваться на сайте."

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Установить новый пароль"
        return context
