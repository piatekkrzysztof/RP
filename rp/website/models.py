from datetime import timedelta

from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone

from django.db.models.signals import post_migrate
from django.dispatch import receiver
from django.core.exceptions import ObjectDoesNotExist


class Tier(models.Model):
    name = models.CharField(max_length=255, unique=True)
    thumbnail_s_height = models.PositiveIntegerField(default=200, validators=[MaxValueValidator(1920)])
    thumbnail_m_height = models.PositiveIntegerField(null=True, default=0)
    orginal_link = models.BooleanField(default=False)
    allow_links = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class User(AbstractUser):
    tier = models.ForeignKey('Tier', on_delete=models.CASCADE, null=True)

    def __str__(self):
        return self.username


class Image(models.Model):
    photo = models.ImageField(upload_to='upimages')
    user = models.ForeignKey('User', on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True, editable=False)


class ExpLink(models.Model):
    image = models.ForeignKey('Image', on_delete=models.CASCADE)
    duration = models.DurationField(default=timedelta(seconds=300),
                                    validators=[MinValueValidator(timedelta(seconds=300)),
                                                MaxValueValidator(timedelta(seconds=30000))])
    expires_at = models.DateTimeField()

    def save(self, *args, **kwargs):
        self.expires_at = timezone.now() + timedelta(seconds=self.duration.total_seconds())
        super().save(*args, **kwargs)


@receiver(post_migrate)
def create_initial_tiers(sender, **kwargs):
    try:
        Tier.objects.get(name='Basic')
    except ObjectDoesNotExist:
        Tier.objects.create(name='Basic', thumbnail_s_height=200, thumbnail_m_height=0, orginal_link=False,
                            allow_links=False)
        Tier.objects.create(name='Premium', thumbnail_s_height=200, thumbnail_m_height=400, orginal_link=True,
                            allow_links=False)
        Tier.objects.create(name='Enterprise', thumbnail_s_height=200, thumbnail_m_height=400, orginal_link=True,
                            allow_links=True)
