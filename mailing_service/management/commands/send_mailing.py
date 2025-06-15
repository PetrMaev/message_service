from django.core.mail import send_mail
from django.core.management.base import BaseCommand

from config.settings import EMAIL_HOST_USER
from mailing_service.models import Mailing


class Command(BaseCommand):
    help = "Отправка рассылки по требованию"

    def handle(self, *args, **kwargs):
        mailing = Mailing.objects.get(id=1)
        message = mailing.message
        subject = message.title
        message_text = message.text
        from_email = EMAIL_HOST_USER
        clients = Mailing.clients.all()
        recipient_list = [client.email for client in clients]
        send_mail(subject, message_text, from_email, recipient_list)

        self.stdout.write(self.style.SUCCESS("Рассылка успешно отправлена!"))
