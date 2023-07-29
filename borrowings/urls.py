from rest_framework import routers

from borrowings.views import BorrowingViewSet

app_name = "borrowings"

router = routers.DefaultRouter()
router.register("", BorrowingViewSet, basename="borrowing")

urlpatterns = [] + router.urls
