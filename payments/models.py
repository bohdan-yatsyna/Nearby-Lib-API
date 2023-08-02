from django.db import models

from borrowings.models import Borrowing


class Payment(models.Model):

    class StatusChoices(models.TextChoices):
        PENDING = "Pending"
        PAID = "Paid"

    class TypeChoices(models.TextChoices):
        PAYMENT = "Payment"
        FINE = "Fine"

    status = models.CharField(max_length=7, choices=StatusChoices.choices)
    type = models.CharField(max_length=7, choices=TypeChoices.choices)
    borrowing_id = models.ForeignKey(
        to=Borrowing,
        on_delete=models.CASCADE,
        related_name="payments",
    )
    session_url = models.CharField(max_length=1000, null=True, blank=True)
    session_id = models.CharField(max_length=1000, null=True, blank=True)
    to_pay = models.DecimalField(max_digits=6, decimal_places=2)

    def __str__(self) -> str:
        return (
            f"Borrowing ID: {self.borrowing_id}, "
            f"payment status: {self.status}"
        )
