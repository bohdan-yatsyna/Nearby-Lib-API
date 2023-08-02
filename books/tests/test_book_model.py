from books.models import Book
from django.test import TestCase


class BookModelTest(TestCase):

    def test_book_str_representation(self):
        book = Book.objects.create(
            title="Shantaram",
            author="Gregory David Roberts",
            cover="Soft",
            inventory=7,
            daily_fee=0.12,
        )
        self.assertEqual(str(book), f"{book.title} ({book.author})")
