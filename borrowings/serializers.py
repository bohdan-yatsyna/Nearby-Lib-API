import datetime

from django.db import transaction
from rest_framework import serializers

from borrowings.models import Borrowing
from notifications.notifications_bot import send_borrowing_create_notification


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
            "user",
            "expected_return_date",
        )
        read_only_fields = ("id", "actual_return_date", "user")

    @transaction.atomic()
    def create(self, validated_data):
        book = validated_data["book"]
        book.inventory -= 1
        book.save()

        borrowing = Borrowing.objects.create(**validated_data)

        send_borrowing_create_notification(
            user=validated_data["user"],
            borrowing=borrowing
        )

        return borrowing

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
        fields = ("actual_return_date",)

    def validate(self, data):
        today = datetime.date.today()

        if data["actual_return_date"] < today:
            raise serializers.ValidationError(
                "Actual return date can not be in the past"
            )

        borrowing_to_return = self.instance
        book = borrowing_to_return.book

        if borrowing_to_return.actual_return_date:
            raise serializers.ValidationError(
                "This book already returned"
            )
        book.inventory += 1
        book.save()

        return data
