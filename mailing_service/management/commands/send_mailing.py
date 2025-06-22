from django.core.mail import send_mail, EmailMessage
from django.core.management.base import BaseCommand

from config.settings import EMAIL_HOST_USER
from mailing_service.models import Mailing, MailingAttempt


class Command(BaseCommand):
    help = "Отправка рассылки по требованию"

    def add_arguments(self, parser):
        parser.add_argument(
            'mailing_id',
            type=int,
            help='mailing number',
        )

    def handle(self, *args, **kwargs):
        mailing_id = kwargs['mailing_id']

        if not Mailing.objects.filter(id=mailing_id).exists():
            self.stdout.write(self.style.ERROR("Такой рассылки не существует"))
            return

        mailing = Mailing.objects.get(id=mailing_id)
        if mailing.status == Mailing.COMPLETED:
            self.stdout.write(self.style.ERROR("Рассылка уже завершена."))
            return

        message = mailing.message
        subject = message.title
        message_text = message.text
        from_email = EMAIL_HOST_USER
        clients = mailing.clients.all()
        recipient_list = [client.email for client in clients]

        mailing.status = Mailing.RUNNING

        try:
            email = EmailMessage(subject=subject, body=message_text, from_email=from_email, to=recipient_list)
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
            mailing_attempt.save()

            send_mail(subject, message_text, from_email, recipient_list)

        except Exception as e:
            # попытка.status ставим fail
            mailing_attempt.status = MailingAttempt.FAIL
            # попытка.mail_server_answer ставим str(e)
            mailing_attempt.mail_server_answer = str(e)
            self.stdout.write(self.style.ERROR(f"Рассылка не завершена, возникла ошибка {str(e)}"))

        else:
            # попытка.status ставим success
            mailing_attempt.status = MailingAttempt.SUCCESS
            mailing.status = Mailing.COMPLETED  # саму рассылку тоже помечаем как завершенную
            self.stdout.write(self.style.SUCCESS("Рассылка успешно отправлена!"))

        mailing_attempt.save()
        mailing.save()
