from enum import StrEnum, auto
from django.db import models


class Cover(StrEnum):
    HARD = auto()
    SOFT = auto()


class Book(models.Model):
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    cover = models.CharField(Cover, max_length=4, blank=False)
    inventory = models.PositiveSmallIntegerField()
    daily_fee = models.DecimalField(max_digits=6, decimal_places=2)

    def __str__(self) -> str:
        return f"{self.title} ({self.author})"
