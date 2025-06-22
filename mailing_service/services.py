from django.core.mail import send_mail
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.utils import timezone

from config.settings import EMAIL_HOST_USER

from .models import Mailing, MailingAttempt


def send_mailing(request, pk):
    mailing = get_object_or_404(Mailing, pk=pk)

    if mailing.status == Mailing.COMPLETED:
        return print("Рассылка уже завершена.")

    message = mailing.message
    subject = message.title
    message_text = message.text
    from_email = EMAIL_HOST_USER
    clients = mailing.clients.all()
    recipient_list = [client.email for client in clients]

    mailing.start = timezone.now()
    mailing.status = Mailing.RUNNING

    owner = request.user
    mailing_attempt = MailingAttempt(
        date=mailing.start,
        mailing=mailing,
        status="",
        mail_server_answer="",
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

    return redirect(reverse("mailing_service:mailing_list"))
