from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from books.models import Book
from books.serializers import BookSerializer

BOOK_LIST_URL = reverse("books:book-list")

BOOK_DATA = {
    "title": "Shantaram",
    "author": "Gregory David Roberts",
    "cover": "Soft",
    "inventory": 7,
    "daily_fee": Decimal("0.12"),
}
NEW_BOOK_DATA = {
    "title": "Shantaram four",
    "author": "Gregory David Roberts",
    "cover": "Soft",
    "inventory": 3,
    "daily_fee": Decimal("0.20"),
}
BOOK_TO_PUT_DATA = {
    "title": "Shantaram five",
    "author": "Gregory David",
    "cover": "Hard",
    "inventory": 4,
    "daily_fee": Decimal("0.13"),
}
BOOK_TO_PATCH_DATA = {
    "title": "Shantaram six",
    "author": "Gregory Ouu",
    "daily_fee": Decimal("0.11"),
}


def sample_book(**params):
    defaults = BOOK_DATA.copy()
    defaults.update(params)
    return Book.objects.create(**defaults)


class UnauthenticatedBookApiTests(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()

    def test_auth_not_required_for_list(self):
        response = self.client.get(BOOK_LIST_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class AuthenticatedBookApiTests(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "test@test.com", "TestPassword1"
        )
        self.client.force_authenticate(self.user)
        self.book_1 = sample_book(title="Shantaram")
        self.book_2 = sample_book(title="Shantaram two")
        self.book_3 = sample_book(title="Shantaram tree")

        self.serializer_1 = BookSerializer(self.book_1)
        self.serializer_2 = BookSerializer(self.book_2)
        self.serializer_3 = BookSerializer(self.book_3)

    def test_standard_users_create_book_forbidden(self):
        response = self.client.post(BOOK_LIST_URL, NEW_BOOK_DATA)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_standard_users_put_book_forbidden(self):
        url = reverse("books:book-detail", args=[self.book_1.id])
        response = self.client.put(url, BOOK_TO_PUT_DATA)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_standard_users_patch_book_forbidden(self):
        url = reverse("books:book-detail", args=[self.book_1.id])
        response = self.client.patch(url, BOOK_TO_PATCH_DATA)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_standard_users_delete_book_forbidden(self):
        book = sample_book()
        url = reverse("books:book-detail", args=[book.id])
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class AdminBookApiTests(TestCase):
    def book_detail_url(self, book_id) -> str:
        return reverse("books:book-detail", args=[book_id])

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.book_1 = sample_book(**BOOK_DATA)
        cls.serializer_1 = BookSerializer(cls.book_1)

    def setUp(self) -> None:
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "test@admin.com",
            "PassWoord1",
            is_staff=True,
        )
        self.client.force_authenticate(self.user)

    def test_admin_users_create_book_allowed(self):
        response = self.client.post(BOOK_LIST_URL, NEW_BOOK_DATA)
        book = Book.objects.get(id=response.data["id"])

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        for key in NEW_BOOK_DATA:
            self.assertEqual(NEW_BOOK_DATA[key], getattr(book, key))

    def test_admin_users_put_book_allowed(self):
        url = self.book_detail_url(self.book_1.id)
        response = self.client.put(url, BOOK_TO_PUT_DATA)

        self.book_1.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for key in BOOK_TO_PUT_DATA:
            self.assertEqual(BOOK_TO_PUT_DATA[key], getattr(self.book_1, key))

    def test_admin_users_patch_book_allowed(self):
        url = self.book_detail_url(self.book_1.id)
        response = self.client.patch(url, BOOK_TO_PATCH_DATA)

        self.book_1.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for key in BOOK_TO_PATCH_DATA:
            self.assertEqual(
                BOOK_TO_PATCH_DATA[key],
                getattr(self.book_1, key),
            )

    def test_admin_users_delete_book_allowed(self):
        book = sample_book()
        url = self.book_detail_url(book.id)
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
