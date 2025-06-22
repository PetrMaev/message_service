from django.db import models

from users.models import CustomUser


class Client(models.Model):
    email = models.EmailField(unique=True)
    full_name = models.CharField(max_length=100, null=True, blank=True, verbose_name="ФИО")
    comment = models.TextField(null=True, blank=True, verbose_name="Комментарий")
    owner = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        verbose_name="Владелец",
        help_text="Укажите владельца получателя рассылки",
        null=True,
        blank=True,
    )

    def __str__(self):
        return self.email

    class Meta:
        verbose_name = "клиент"
        verbose_name_plural = "клиенты"
        ordering = [
            "email",
        ]


class Message(models.Model):
    title = models.CharField(max_length=150, null=True, blank=True, verbose_name="Тема письма")
    text = models.TextField(null=True, blank=True, verbose_name="Текст письма")
    owner = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        verbose_name="Владелец",
        help_text="Укажите владельца сообщения",
        null=True,
        blank=True,
    )

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "сообщение"
        verbose_name_plural = "сообщения"
        ordering = [
            "title",
        ]


class Mailing(models.Model):
    CREATED = "created"
    RUNNING = "running"
    COMPLETED = "completed"

    STATUS_CHOICES = [
        (CREATED, "Создана"),
        (RUNNING, "Запущена"),
        (COMPLETED, "Завершена"),
    ]

    start = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Дата и время первой отправки",
        help_text="Укажите дату и время первой отправки в формате: YYYY-MM-DD HH:MM:SS",
    )
    end = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Дата и время окончания отправки",
        help_text="Укажите дату и время окончания отправки в формате: YYYY-MM-DD HH:MM:SS",
    )
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=CREATED, verbose_name="Статус рассылки")
    message = models.ForeignKey(Message, on_delete=models.CASCADE, related_name="message", verbose_name="Сообщение")
    clients = models.ManyToManyField(Client, related_name="clients", verbose_name="Получатели")
    is_active = models.BooleanField(default=True)
    owner = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        verbose_name="Владелец",
        help_text="Укажите владельца рассылки",
        null=True,
        blank=True,
    )

    def __str__(self):
        return (
            f""
            f"Статус: {self.status} - "
            f"Дата и время отправки: {self.start}, "
            f"Дата и время окончания отправки: {self.end}"
        )

    class Meta:
        verbose_name = "рассылка"
        verbose_name_plural = "рассылки"
        permissions = [
            ("can_deactivation_mailing", "Can deactivation mailing"),
        ]


class MailingAttempt(models.Model):
    SUCCESS = "success"
    FAIL = "fail"

    STATUS_CHOICES = [
        (SUCCESS, "Успешно"),
        (FAIL, "Не успешно"),
    ]

    date = models.DateTimeField(verbose_name="Дата и время попытки")
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, verbose_name="Статус попытки рассылки")
    mail_server_answer = models.TextField(verbose_name="Ответ почтового сервера")
    mailing = models.ForeignKey(Mailing, on_delete=models.CASCADE, related_name="mailing", verbose_name="Рассылка")

    owner = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        verbose_name="Владелец",
        null=True,
        blank=True,
    )

    def __str__(self):
        return f"Статус: {self.status} - Дата и время попытки: {self.date}"

    class Meta:
        verbose_name = "попытка рассылки"
        verbose_name_plural = "попытки рассылки"
