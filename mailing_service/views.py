from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.core.mail import EmailMessage, send_mail
from django.http import HttpResponseForbidden
from django.shortcuts import render
from django.urls import reverse, reverse_lazy
from django.views.generic import DetailView, ListView, TemplateView
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator
from django.core.cache import cache

from config.settings import EMAIL_HOST_USER

from .forms import ClientForm, MailingAttemptForm, MailingForm, MailingUpdateForm, MessageForm
from .models import Client, Mailing, MailingAttempt, Message


class HomeTemplateView(TemplateView):
    template_name = "mailing_service/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            context.update(
                {
                    "mailings": Mailing.objects.filter(owner=self.request.user).count,
                    "mailings_run": Mailing.objects.filter(status="running", owner=self.request.user).count,
                    "clients": Client.objects.filter(owner=self.request.user).count,
                }
            )

        return context


# Получатели рассылки
class ClientCreateView(CreateView):
    model = Client
    form_class = ClientForm
    template_name = "mailing_service/client_form.html"
    success_url = reverse_lazy("mailing_service:home")

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class ClientUpdateView(UpdateView):
    model = Client
    form_class = ClientForm
    template_name = "mailing_service/client_edit.html"

    def test_func(self):
        client = self.get_object()
        return client.owner == self.request.user or self.request.user.has_perm("mailing_service.change_client")

    def handle_no_permission(self):
        raise PermissionDenied("У вас нет прав на редактирование этого клиента")

    def custom_permission_denied(request, exception=None):
        return HttpResponseForbidden(render(request, "403.html"))

    def get_success_url(self):
        return reverse("mailing_service:client_detail", kwargs={"pk": self.object.pk})


class ClientDeleteView(DeleteView):
    model = Client
    template_name = "mailing_service/client_confirm_delete.html"
    success_url = reverse_lazy("mailing_service:home")

    def test_func(self):
        client = self.get_object()
        return client.owner == self.request.user or self.request.user.has_perm("mailing_service.delete_client")

    def handle_no_permission(self):
        raise PermissionDenied("У вас нет прав на удаление этого клиента")

    def custom_permission_denied(request, exception=None):
        return HttpResponseForbidden(render(request, "403.html"))


class ClientListView(LoginRequiredMixin, ListView):
    model = Client
    template_name = "mailing_service/client_list.html"
    context_object_name = "clients"


class ClientDetailView(DetailView):
    model = Client
    template_name = "mailing_service/client_detail.html"
    context_object_name = "client"

    def test_func(self):
        client = self.get_object()
        return client.owner == self.request.user or self.request.user.has_perm("mailing_service.view_client")

    def handle_no_permission(self):
        raise PermissionDenied("У вас нет прав на просмотр данных этого клиента")

    def custom_permission_denied(request, exception=None):
        return HttpResponseForbidden(render(request, "403.html"))


# Сообщение
class MessageCreateView(CreateView):
    model = Message
    form_class = MessageForm
    template_name = "mailing_service/message_form.html"
    success_url = reverse_lazy("mailing_service:home")

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class MessageUpdateView(UpdateView):
    model = Message
    form_class = MessageForm
    template_name = "mailing_service/message_edit.html"

    def test_func(self):
        message = self.get_object()
        return message.owner == self.request.user or self.request.user.has_perm("mailing_service.change_message")

    def handle_no_permission(self):
        raise PermissionDenied("У вас нет прав на редактирование этого сообщения")

    def custom_permission_denied(request, exception=None):
        return HttpResponseForbidden(render(request, "403.html"))

    def get_success_url(self):
        return reverse("mailing_service:message_detail", kwargs={"pk": self.object.pk})


class MessageDeleteView(DeleteView):
    model = Message
    template_name = "mailing_service/message_confirm_delete.html"
    success_url = reverse_lazy("mailing_service:home")

    def test_func(self):
        message = self.get_object()
        return message.owner == self.request.user or self.request.user.has_perm("mailing_service.delete_message")

    def handle_no_permission(self):
        raise PermissionDenied("У вас нет прав на удаление этого сообщения")

    def custom_permission_denied(request, exception=None):
        return HttpResponseForbidden(render(request, "403.html"))


class MessageListView(LoginRequiredMixin, ListView):
    model = Message
    template_name = "mailing_service/message_list.html"
    context_object_name = "messages"


class MessageDetailView(DetailView):
    model = Message
    template_name = "mailing_service/message_detail.html"
    context_object_name = "message"

    def test_func(self):
        message = self.get_object()
        return message.owner == self.request.user or self.request.user.has_perm("mailing_service.view_message")

    def handle_no_permission(self):
        raise PermissionDenied("У вас нет прав на просмотр этого сообщения")

    def custom_permission_denied(request, exception=None):
        return HttpResponseForbidden(render(request, "403.html"))


# Рассылка
class MailingCreateView(CreateView):
    model = Mailing
    form_class = MailingForm
    template_name = "mailing_service/mailing_form.html"
    success_url = reverse_lazy("mailing_service:home")

    def form_valid(self, form):
        form.instance.owner = self.request.user
        # Сохраняем объект, чтобы получить id
        mailing = form.save()
        # Получаем объект сообщения через ForeignKey
        message = mailing.message
        subject = message.title
        message_text = message.text
        from_email = EMAIL_HOST_USER
        clients = form.cleaned_data["clients"]
        recipient_list = [client.email for client in clients]
        send_mail(subject, message_text, from_email, recipient_list)
        # Добавляем получателей после сохранения
        mailing.clients.set(clients)
        mailing_attempt = form.save()
        email = EmailMessage(subject=subject, body=message_text, from_email=from_email, to=recipient_list)
        try:
            response = email.send(fail_silently=False)
            # Проверяем, если количество отправленных писем равно количеству адресатов
            if response == len(recipient_list):
                status = "Успешно"
            else:
                status = "Не успешно"
            owner = self.request.user
            mailing_attempt = MailingAttempt(
                date=mailing.start, mailing=mailing, status=status, mail_server_answer=response, owner=owner
            )
        except Exception as e:
            # Если произошла ошибка, выводим её сообщение
            print(f"Ошибка отправки: {e}")

        mailing_attempt.save()
        return super().form_valid(form)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({"request": self.request})
        return kwargs


class MailingUpdateView(UpdateView):
    model = Mailing
    form_class = MailingUpdateForm
    template_name = "mailing_service/mailing_edit.html"

    def test_func(self):
        mailing = self.get_object()
        return mailing.owner == self.request.user or self.request.user.has_perm("mailing_service.change_mailing")

    def handle_no_permission(self):
        raise PermissionDenied("У вас нет прав на редактирование этой рассылки")

    def custom_permission_denied(request, exception=None):
        return HttpResponseForbidden(render(request, "403.html"))

    def get_success_url(self):
        return reverse("mailing_service:mailing_detail", kwargs={"pk": self.object.pk})


class MailingDeleteView(DeleteView):
    model = Mailing
    template_name = "mailing_service/mailing_confirm_delete.html"
    success_url = reverse_lazy("mailing_service:home")

    def test_func(self):
        mailing = self.get_object()
        return mailing.owner == self.request.user or self.request.user.has_perm("mailing_service.delete_mailing")

    def handle_no_permission(self):
        raise PermissionDenied("У вас нет прав на удаление этой рассылки")

    def custom_permission_denied(request, exception=None):
        return HttpResponseForbidden(render(request, "403.html"))


@method_decorator(cache_page(60), name='dispatch')
class MailingListView(LoginRequiredMixin, ListView):
    model = Mailing
    template_name = "mailing_service/mailing_list.html"
    context_object_name = "mailings"


class MailingDetailView(DetailView):
    model = Mailing
    template_name = "mailing_service/mailing_detail.html"
    context_object_name = "mailing"

    def test_func(self):
        mailing = self.get_object()
        return mailing.owner == self.request.user or self.request.user.has_perm("mailing_service.view_mailing")

    def handle_no_permission(self):
        raise PermissionDenied("У вас нет прав на просмотр этой рассылки")

    def custom_permission_denied(request, exception=None):
        return HttpResponseForbidden(render(request, "403.html"))


# Попытка рассылки
class MailingAttemptCreateView(CreateView):
    model = MailingAttempt
    form_class = MailingAttemptForm

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({"request": self.request})
        return kwargs


@method_decorator(cache_page(60), name='dispatch')
class MailingAttemptListView(LoginRequiredMixin, ListView):
    model = MailingAttempt
    template_name = "mailing_service/attempt_list.html"
    context_object_name = "attempts"


class MailingAttemptDetailView(LoginRequiredMixin, DetailView):
    model = MailingAttempt
    template_name = "mailing_service/attempt_detail.html"
    context_object_name = "attempt"
