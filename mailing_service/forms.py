from django import forms
from django.forms import BooleanField

from mailing_service.models import Client, Mailing, MailingAttempt, Message


class StyleFormMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for fild_name, fild in self.fields.items():
            if isinstance(fild, BooleanField):
                fild.widget.attrs["class"] = "form-check-input"
            else:
                fild.widget.attrs["class"] = "form-control"


class ClientForm(StyleFormMixin, forms.ModelForm):
    class Meta:
        model = Client
        fields = ["email", "full_name", "comment"]


class MessageForm(StyleFormMixin, forms.ModelForm):
    class Meta:
        model = Message
        fields = ["title", "text"]


class MailingForm(StyleFormMixin, forms.ModelForm):

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request")
        user = self.request.user
        super().__init__(*args, **kwargs)
        self.fields["clients"].queryset = Client.objects.filter(owner=user)
        self.fields["message"].queryset = Message.objects.filter(owner=user)

    class Meta:
        model = Mailing
        fields = ["start", "end", "status", "message", "clients"]


class MailingUpdateForm(StyleFormMixin, forms.ModelForm):
    class Meta:
        model = Mailing
        fields = ["start", "end", "status", "message", "clients", "is_active"]


class MailingAttemptForm(StyleFormMixin, forms.ModelForm):

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request")
        user = self.request.user
        super().__init__(*args, **kwargs)
        self.fields["mailing"].queryset = Mailing.objects.filter(owner=user)

    class Meta:
        model = MailingAttempt
        fields = ["date", "status", "mail_server_answer", "mailing", "owner"]
