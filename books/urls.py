from rest_framework import routers

from books.views import BookViewSet

app_name = "books"

router = routers.DefaultRouter()
router.register("books", BookViewSet, basename="book")

urlpatterns = [] + router.urls
