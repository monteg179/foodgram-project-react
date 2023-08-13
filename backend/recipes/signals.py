import os

from django.db.models.signals import post_delete
from django.dispatch import receiver

from recipes.models import Recipe


@receiver(post_delete, sender=Recipe)
def recipe_delete_callback(sender, instance: Recipe, **kwargs):
    if os.path.isfile(instance.image.path):
        os.remove(instance.image.path)
