from django.test import TestCase
from django.contrib.auth import get_user_model
from books.models import Book
from borrowings.models import Borrowing


class BorrowingModelTest(TestCase):

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

    def test_borrowing_str_representation(self):
        borrowing = Borrowing.objects.create(
            expected_return_date="2023-10-25",
            book=self.book,
            user=self.user,
        )

        expected_str_representation = (
            f"Book: {self.book.title} ({self.book.author}) "
            f"borrowed by {self.user.first_name} {self.user.last_name}."
            f"Expected return date: {borrowing.expected_return_date}"
        )
        self.assertEqual(str(borrowing), expected_str_representation)
