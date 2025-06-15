from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand


class Command(BaseCommand):

    def handle(self, *args, **options):
        User = get_user_model()
        user = User.objects.create(
            email="manager@sky.pro",
            first_name="Manager",
        )
        user.set_password("123qwe")
        user.is_active = True
        user.save()
        managers_group = Group.objects.create(name="Managers")
        user.groups.add(managers_group)
        user.save()

        self.stdout.write(self.style.SUCCESS(f"Successfully created manager user with email {user.email}"))
