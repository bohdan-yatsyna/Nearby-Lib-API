from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _

from books.models import Book


class Borrowing(models.Model):
    borrow_date = models.DateField(auto_now_add=True)
    expected_return_date = models.DateField(blank=False, null=False)
    actual_return_date = models.DateField()
    book = models.ForeignKey(
        to=Book,
        on_delete=models.PROTECT,
        related_name="borrowings",
    )
    user = models.ForeignKey(
        get_user_model(),
        on_delete=models.PROTECT,
        related_name="borrowings",
    )

    class Meta:
        ordering = ["expected_return_date"]

    def clean(self) -> None:
        if self.expected_return_date <= self.borrow_date:
            raise ValidationError(_(
                "Expected return date has to be after the borrowing date."
            ))

        if self.actual_return_date and (
            self.actual_return_date < self.borrow_date
        ):
            raise ValidationError(_(
                "Actual returning date cannot be earlier "
                "than the borrowing date."
            ))

    def save(self, *args, **kwargs) -> None:
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return (
            f"Book: {self.book.title} ({self.book.author}) "
            f"borrowed by {self.user.first_name} {self.user.last_name}."
            f"Expected return date: {self.expected_return_date}"
        )
