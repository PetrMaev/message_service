from django.urls import path

from mailing_service.apps import MailingServiceConfig

from .views import (ClientCreateView, ClientDeleteView, ClientDetailView, ClientListView, ClientUpdateView,
                    HomeTemplateView, MailingAttemptDetailView, MailingAttemptListView, MailingCreateView,
                    MailingDeleteView, MailingDetailView, MailingListView, MailingUpdateView, MessageCreateView,
                    MessageDeleteView, MessageDetailView, MessageListView, MessageUpdateView)

app_name = MailingServiceConfig.name

urlpatterns = [
    path("", HomeTemplateView.as_view(), name="home"),
    path("mailing_service/client/new/", ClientCreateView.as_view(), name="client_create"),
    path("mailing_service/client/<int:pk>/edit/", ClientUpdateView.as_view(), name="client_edit"),
    path("mailing_service/client/<int:pk>/delete/", ClientDeleteView.as_view(), name="client_delete"),
    path("mailing_service/client_list/", ClientListView.as_view(), name="client_list"),
    path("mailing_service/client_detail/<int:pk>/", ClientDetailView.as_view(), name="client_detail"),
    path("mailing_service/message/new/", MessageCreateView.as_view(), name="message_create"),
    path("mailing_service/message/<int:pk>/edit/", MessageUpdateView.as_view(), name="message_edit"),
    path("mailing_service/message/<int:pk>/delete/", MessageDeleteView.as_view(), name="message_delete"),
    path("mailing_service/message_list/", MessageListView.as_view(), name="message_list"),
    path("mailing_service/message_detail/<int:pk>/", MessageDetailView.as_view(), name="message_detail"),
    path("mailing_service/mailing/new/", MailingCreateView.as_view(), name="mailing_create"),
    path("mailing_service/mailing/<int:pk>/edit/", MailingUpdateView.as_view(), name="mailing_edit"),
    path("mailing_service/mailing/<int:pk>/delete/", MailingDeleteView.as_view(), name="mailing_delete"),
    path("mailing_service/mailing_list/", MailingListView.as_view(), name="mailing_list"),
    path("mailing_service/mailing_detail/<int:pk>/", MailingDetailView.as_view(), name="mailing_detail"),
    path("mailing_service/attempt_detail/<int:pk>/", MailingAttemptDetailView.as_view(), name="attempt_detail"),
    path("mailing_service/attempt_list/", MailingAttemptListView.as_view(), name="attempt_list"),
]
