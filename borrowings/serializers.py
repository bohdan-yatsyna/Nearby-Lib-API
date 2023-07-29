from django.db import transaction
from rest_framework import serializers

from borrowings.models import Borrowing


class BorrowingListSerializer(serializers.ModelSerializer):
    book = serializers.CharField(source="book.title", read_only=True)

    class Meta:
        model = Borrowing
        fields = (
            "id",
            "borrow_date",
            "expected_return_date",
            "actual_return_date",
            "book",
        )


class BorrowingDetailSerializer(BorrowingListSerializer):
    user = serializers.CharField(source="user.full_name", read_only=True)

    class Meta:
        model = Borrowing
        fields = (
            "id",
            "borrow_date",
            "expected_return_date",
            "actual_return_date",
            "book",
            "user"
        )


class CreateBorrowingSerializer(serializers.ModelSerializer):

    class Meta:
        model = Borrowing
        fields = (
            "book",
            "expected_return_date",
        )

    @transaction.atomic()
    def create(self, validated_data):
        book = validated_data["book"]
        book.inventory -= 1
        book.save()

        return super().create(validated_data)

    def validate(self, data):
        book = data.get("book")

        if book.inventory == 0:
            raise serializers.ValidationError(
                "This book is not available for borrowing now"
            )

        return data


class BorrowingReturnSerializer(serializers.ModelSerializer):

    class Meta:
        model = Borrowing
        fields = ("id", "actual_return_date")
