from django.conf import settings
from django.db import models


class Project(models.Model):
    name = models.CharField(max_length=120)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="projects",
    )

    class Meta:
        unique_together = ("name", "owner")
        ordering = ["name"]

    def __str__(self):
        return self.name
