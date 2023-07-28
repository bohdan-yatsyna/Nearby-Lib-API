from django.contrib import admin

from books.models import Book


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    search_fields = ("title", "author")
    list_filter = ("title", "author", "inventory", "daily_fee")
