from datetime import date, timedelta

from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from books.models import Book


class Borrowing(models.Model):
    borrow_date = models.DateField(auto_now_add=True)
    expected_return_date = models.DateField(
        validators=[
            MinValueValidator(limit_value=date.today() + timedelta(days=1)),
            MaxValueValidator(limit_value=date.today() + timedelta(days=30)),
        ],
        help_text=_(
            "Expected return date must be in range from 1 to 30 days "
            "after the borrowing date."
        ),
        blank=False,
        null=False,
    )
    actual_return_date = models.DateField(
        validators=[
            MinValueValidator(limit_value=date.today())
        ],
        help_text=_(
            "Actual returning date can not be earlier the borrowing date."
        ),
    )
    book = models.ForeignKey(
        to=Book,
        on_delete=models.PROTECT,
        related_name="borrowings",
    )
    user = models.ForeignKey(
        to=get_user_model(),
        on_delete=models.PROTECT,
        related_name="borrowings",
    )

    class Meta:
        ordering = ["expected_return_date"]

    def __str__(self) -> str:
        return (
            f"Book: {self.book.title} ({self.book.author}) "
            f"borrowed by {self.user.first_name} {self.user.last_name}."
            f"Expected return date: {self.expected_return_date}"
        )
