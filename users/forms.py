from django import forms
from django.contrib.auth.forms import PasswordResetForm, SetPasswordForm, UserCreationForm
from django.forms import BooleanField

from users.models import CustomUser


class StyleFormMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for fild_name, fild in self.fields.items():
            if isinstance(fild, BooleanField):
                fild.widget.attrs["class"] = "form-check-input"
            else:
                fild.widget.attrs["class"] = "form-control"


class CustomUserCreationForm(StyleFormMixin, UserCreationForm):
    phone_number = forms.CharField(
        max_length=15,
        required=False,
        label="Номер телефона",
        help_text="Введите свой номер телефона. Необязательное поле.",
    )

    country = forms.CharField(
        max_length=15,
        required=False,
        label="Страна",
        help_text="Укажите свою страну. Необязательное поле.",
    )

    class Meta:
        model = CustomUser
        fields = ("email", "avatar", "phone_number", "country", "password1", "password2")

    def clean_phone_number(self):
        phone_number = self.cleaned_data.get("phone_number")
        if phone_number and not phone_number.isdigit():
            raise forms.ValidationError("Номер телефона должен состоять только из цифр")
        return phone_number


class CustomUserUpdateForm(StyleFormMixin, forms.ModelForm):
    phone_number = forms.CharField(
        max_length=15,
        required=False,
        label="Номер телефона",
        help_text="Введите свой номер телефона. Необязательное поле.",
    )

    country = forms.CharField(
        max_length=15,
        required=False,
        label="Страна",
        help_text="Укажите свою страну. Необязательное поле.",
    )

    class Meta:
        model = CustomUser
        fields = ("email", "avatar", "phone_number", "country", "is_active")

    def clean_phone_number(self):
        phone_number = self.cleaned_data.get("phone_number")
        if phone_number and not phone_number.isdigit():
            raise forms.ValidationError("Номер телефона должен состоять только из цифр")
        return phone_number


class UserPasswordChangeForm(SetPasswordForm):
    """Форма изменения пароля"""

    def __init__(self, *args, **kwargs):
        """Обновление стилей формы"""
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({"class": "form-control", "autocomplete": "off"})


class UserForgotPasswordForm(PasswordResetForm):
    """Запрос на восстановление пароля"""

    def __init__(self, *args, **kwargs):
        """Обновление стилей формы"""
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({"class": "form-control", "autocomplete": "off"})


class UserSetNewPasswordForm(SetPasswordForm):
    """Изменение пароля пользователя после подтверждения"""

    def __init__(self, *args, **kwargs):
        """Обновление стилей формы"""
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({"class": "form-control", "autocomplete": "off"})
