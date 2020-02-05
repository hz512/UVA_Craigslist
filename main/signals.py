from django.db.models.signals import post_save
from django.dispatch import receiver
from users.models import CustomUser
from .models import Profile, Cart


@receiver(post_save, sender=CustomUser)
def create_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=CustomUser)
def save_profile(sender, instance, **kwargs):
    instance.profile.save()


@receiver(post_save, sender=CustomUser)
def create_cart(sender, instance, created, **kwargs):
    if created:
        Cart.objects.create(owner=instance)


@receiver(post_save, sender=CustomUser)
def save_cart(sender, instance, **kwargs):
    instance.profile.save()