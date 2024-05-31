from django.db import models


class BaseModelManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(deleted__isnull=True).order_by("-pk")


class BaseModel(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    deleted = models.DateTimeField(null=True, blank=True)

    objects = BaseModelManager()
    all_objects = models.Manager()

    class Meta:
        abstract = True
        ordering = ["-pk"]
