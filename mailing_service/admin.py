from django.contrib import admin

from .models import Client, Mailing, MailingAttempt, Message


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ("id", "email", "full_name", "owner")
    search_fields = ("email", "full_name")


@admin.register(Mailing)
class MailingAdmin(admin.ModelAdmin):
    list_display = ("id", "start", "end", "status", "owner")


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "owner")


@admin.register(MailingAttempt)
class MailingAttemptAdmin(admin.ModelAdmin):
    list_display = ("id", "date", "status", "mail_server_answer", "mailing", "owner")
