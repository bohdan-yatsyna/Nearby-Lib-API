import datetime
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from books.models import Book
from books.serializers import BookSerializer
from borrowings.models import Borrowing
from borrowings.serializers import BorrowingListSerializer

BORROWING_LIST_URL = reverse("borrowings:borrowing-list")


def detail_url(borrowing_id):
    return reverse("borrowings:borrowing-detail", args=[borrowing_id])


def sample_book(**params):
    defaults = {
        "title": "Shantaram",
        "author": "Gregory David Roberts",
        "cover": "Soft",
        "inventory": 1,
        "daily_fee": Decimal("0.12"),
    }
    defaults.update(params)

    return Book.objects.create(**defaults)


class UnauthenticatedUsersBorrowingApiTests(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()

    def test_auth_required(self):
        response = self.client.get(BORROWING_LIST_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedUsersBorrowingApiTests(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.user_1 = get_user_model().objects.create_user(
            "test@admin.com", "TestPassword1", is_staff=True
        )
        self.user_2 = get_user_model().objects.create_user(
            "test@standard.com", "PassWoorD1"
        )
        self.book_1 = sample_book(title="Shantaram")
        self.book_2 = sample_book(title="Shantaram two")
        self.serializer_1 = BookSerializer(self.book_1)
        self.serializer_2 = BookSerializer(self.book_2)

        self.client.force_authenticate(self.user_1)
        self.borrowed_book_1 = Borrowing.objects.create(
            book=self.book_1,
            user=self.user_1,
            expected_return_date=(
                datetime.date.today() + datetime.timedelta(days=12)
            ),
        )
        self.serializer_borrowed_1 = BorrowingListSerializer(
            self.borrowed_book_1
        )

    def test_list_borrowings_for_authenticated_users_allowed(self):
        response = self.client.get(BORROWING_LIST_URL)
        borrowed_books = Borrowing.objects.filter(user=self.user_1)
        serializer = BorrowingListSerializer(borrowed_books, many=True)

        self.assertEqual(response.data, serializer.data)

    def test_retrieve_borrowings_for_authenticated_users_allowed(self):
        response = self.client.get(detail_url(self.borrowed_book_1.id))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_adding_borrowing_only_to_own_profile(self):
        new_borrowing = {
            "book": self.book_2.id,
            "user": self.user_2.id,
            "expected_return_date": (
                datetime.date.today() + datetime.timedelta(days=15)
            ),
        }
        response = self.client.post(BORROWING_LIST_URL, new_borrowing)
        borrowings = Borrowing.objects.filter(user=self.user_1)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(borrowings)
        self.assertEqual(Book.objects.get(pk=self.book_2.id).inventory, 0)

    def test_creating_borrowing_decrease_book_inventory(self):
        new_borrowing = {
            "book": self.book_2.id,
            "user": self.user_2.id,
            "expected_return_date": (
                datetime.date.today() + datetime.timedelta(days=11)
            ),
        }
        response = self.client.post(BORROWING_LIST_URL, new_borrowing)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Book.objects.get(pk=self.book_2.id).inventory, 0)

    def test_filter_borrowings_by_is_active(self):
        response = self.client.get(BORROWING_LIST_URL, {"is_active": "True"})

        self.assertIn(self.serializer_borrowed_1.data, response.data)

    def test_filter_borrowings_by_user_id_for_admin_users(self):
        response = self.client.get(BORROWING_LIST_URL, {"user_id": "2"})
        borrowed_books = Borrowing.objects.filter(user=self.user_2)
        serializer = BorrowingListSerializer(borrowed_books, many=True)

        self.assertEqual(serializer.data, response.data)

    def test_return_book(self):
        url = f"/api/borrowings/{self.borrowed_book_1.pk}/return/"
        return_date = datetime.date.today()
        data = {"actual_return_date": return_date}
        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.borrowed_book_1.refresh_from_db()
        self.assertIsNotNone(self.borrowed_book_1.actual_return_date)

        self.book_1.refresh_from_db()
        self.assertEqual(self.book_1.inventory, 2)
