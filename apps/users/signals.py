from django.conf import settings
from django.core.mail import EmailMessage
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from apps.files.models import Category, Media, MediaPermission, Tag

# Import your Channel and User models
from .models import Channel, User # Assuming these are in the same app or correctly imported

@receiver(post_save, sender=User)
def post_user_create(sender, instance, created, **kwargs):
    # create a Channel object upon user creation, name it default
    if created:
        new = Channel.objects.create(title="default", user=instance)
        new.save()
        if settings.ADMINS_NOTIFICATIONS.get("NEW_USER", False):
            title = f"[{settings.PORTAL_NAME}] - New user just registered"
            msg = """
User has just registered with email %s\n
Visit user profile page at %s
            """ % (
                instance.email,
                settings.FRONTEND_URL + instance.get_absolute_url(),
            )
            email = EmailMessage(title, msg, settings.DEFAULT_FROM_EMAIL, settings.ADMIN_EMAIL_LIST)
            email.send(fail_silently=True)


@receiver(post_delete, sender=User)
def delete_content(sender, instance, **kwargs):
    """Delete user related content
    Upon user deletion
    """

    Media.objects.filter(user=instance).delete()
    Tag.objects.filter(user=instance).delete()
    Category.objects.filter(user=instance).delete()
