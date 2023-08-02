import datetime

from decimal import Decimal
from django.contrib.auth import get_user_model
from django.test import TestCase

from books.models import Book
from borrowings.models import Borrowing
from payments.models import Payment


class PaymentModelTest(TestCase):
    def setUp(self) -> None:
        self.book = Book.objects.create(
            title="Shantaram",
            author="Gregory David Roberts",
            cover=Book.CoverChoices.SOFT,
            inventory=7,
            daily_fee=0.12,
        )

        self.user = get_user_model().objects.create_user(
            "test@test.com", "TestPassword1"
        )

        self.borrowing = Borrowing.objects.create(
            expected_return_date=(
                datetime.date.today() + datetime.timedelta(days=15)
            ),
            book=self.book,
            user=self.user,
        )

    def test_payment_str_representation(self):
        payment = Payment.objects.create(
            status=Payment.StatusChoices.PENDING,
            type=Payment.TypeChoices.PAYMENT,
            borrowing_id=self.borrowing,
            to_pay=Decimal("12.55"),
        )
        expected_str_representation = (
            f"Borrowing ID: {self.borrowing}, "
            f"payment status: {Payment.StatusChoices.PENDING}"
        )

        self.assertEqual(str(payment), expected_str_representation)
