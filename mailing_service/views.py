from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.core.mail import send_mail
from django.http import HttpResponseForbidden
from django.shortcuts import render
from django.urls import reverse, reverse_lazy
from django.views.generic import DetailView, ListView, TemplateView, View
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator
from django.utils import timezone
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
        return super().form_valid(form)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({"request": self.request})
        return kwargs


# Контроллер отправки
class MailingSendView(View):
    model = Mailing
    success_url = reverse_lazy("mailing_service:mailing_list")

    def post(self, request, **kwargs):
        mailing_id = kwargs['pk']
        mailing = Mailing.objects.get(id=mailing_id)

        message = mailing.message
        subject = message.title
        message_text = message.text
        from_email = EMAIL_HOST_USER
        clients = mailing.clients.all()
        recipient_list = [client.email for client in clients]

        mailing.start = timezone.now()
        mailing.status = Mailing.RUNNING

        owner = self.request.user
        mailing_attempt = MailingAttempt(
            date=mailing.start,
            mailing=mailing,
            status='',
            mail_server_answer='',
            owner=owner
        )
        mailing_attempt.save()

        try:
            send_mail(subject, message_text, from_email, recipient_list)

            mailing_attempt.status = MailingAttempt.SUCCESS
            mailing.status = Mailing.COMPLETED  # саму рассылку тоже помечаем как завершенную

        except Exception as e:
            # попытка.status ставим fail
            mailing_attempt.status = MailingAttempt.FAIL
            # попытка.mail_server_answer ставим str(e)
            mailing_attempt.mail_server_answer = str(e)

        else:
            # попытка.status ставим success
            mailing_attempt.status = MailingAttempt.SUCCESS
            mailing_attempt.mail_server_answer = "Доставлено"
            mailing.status = Mailing.COMPLETED  # саму рассылку тоже помечаем как завершенную
            mailing.end = timezone.now()

        mailing_attempt.save()
        mailing.save()

        return render(request, "mailing_service/mailing_list.html")


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


# @method_decorator(cache_page(60), name='dispatch')
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


# @method_decorator(cache_page(60), name='dispatch')
class MailingAttemptListView(LoginRequiredMixin, ListView):
    model = MailingAttempt
    template_name = "mailing_service/attempt_list.html"
    context_object_name = "attempts"


class MailingAttemptDetailView(LoginRequiredMixin, DetailView):
    model = MailingAttempt
    template_name = "mailing_service/attempt_detail.html"
    context_object_name = "attempt"
