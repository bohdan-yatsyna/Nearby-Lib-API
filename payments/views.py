from typing import Type

from rest_framework import mixins
from rest_framework.permissions import IsAuthenticated
from rest_framework.serializers import Serializer
from rest_framework.viewsets import GenericViewSet
from rest_framework_simplejwt.authentication import JWTAuthentication

from payments.models import Payment
from payments.serializers import PaymentSerializer, PaymentDetailSerializer


class PaymentViewSet(
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    GenericViewSet
):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get_serializer_class(self) -> Type[Serializer]:

        if self.action == "retrieve":
            return PaymentDetailSerializer

        return PaymentSerializer
