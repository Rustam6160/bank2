from django.conf import settings
from django.dispatch import receiver
from django.db.models.signals import post_save

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def add_user_post_save(created, **kwargs):
    instance = kwargs['instance']
    if created:
        print(f'Пользователь {instance.username} был создан.')
    else:
        print(f'Пользователь {instance.username} был создан.')