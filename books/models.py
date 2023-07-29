from django.db import models


class Book(models.Model):

    class CoverChoices(models.Choices):
        HARD = "Hard"
        SOFT = "Soft"

    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    cover = models.CharField(max_length=4, choices=CoverChoices.choices)
    inventory = models.PositiveSmallIntegerField()
    daily_fee = models.DecimalField(max_digits=6, decimal_places=2)

    class Meta:
        ordering = ["author"]

    def __str__(self) -> str:
        return f"{self.title} ({self.author})"
