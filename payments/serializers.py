from rest_framework import serializers

from borrowings.serializers import BorrowingDetailSerializer
from payments.models import Payment


class PaymentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Payment
        fields = (
            "id",
            "status",
            "type",
            "borrowing_id",
            "session_url",
            "session_id",
            "to_pay",
        )


class PaymentDetailSerializer(PaymentSerializer):
    borrowing_id = BorrowingDetailSerializer(many=False, read_only=True)

    class Meta:
        model = Payment
        fields = (
            "id",
            "status",
            "type",
            "borrowing_id",
            "session_url",
            "session_id",
            "to_pay",
        )
