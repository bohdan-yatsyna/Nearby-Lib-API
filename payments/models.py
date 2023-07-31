from django.db import models

from borrowings.models import Borrowing


class Payment(models.Model):

    class StatusChoice(models.TextChoices):
        PENDING = "Pending"
        PAID = "Paid"

    class TypeStatus(models.TextChoices):
        PAYMENT = "Payment"
        FINE = "Fine"

    status = models.CharField(max_length=7, choices=StatusChoice.choices)
    type = models.CharField(max_length=6, choices=TypeStatus.choices)
    borrowing_id = models.ForeignKey(
        to=Borrowing,
        on_delete=models.CASCADE,
    )
    session_url = models.CharField(max_length=500, null=True, blank=True)
    session_id = models.CharField(max_length=500, null=True, blank=True)
    to_pay = models.DecimalField(decimal_places=2, max_digits=6)
