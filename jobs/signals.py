from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Job
from django.contrib.auth import get_user_model
from .utils import send_offer_notification

User = get_user_model()

@receiver(post_save, sender=Job)
def notify_users_of_new_offer(sender, instance, created, **kwargs):
    if created:
        interested_users = User.objects.filter(
            interests__icontains=instance.title  # Matching simple
        )
        for user in interested_users:
            send_offer_notification(user.email, instance)
