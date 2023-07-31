import datetime

from borrowings.models import Borrowing
from celery import shared_task

from notifications.notifications_bot import send_message


@shared_task
def check_overdue_borrowings_with_notification() -> None:
    today = datetime.date.today()
    overdue_borrowings = Borrowing.objects.filter(
        actual_return_date__isnull=True,
        expected_return_date_lte=(today + datetime.timedelta(days=1)),
    )

    if overdue_borrowings:
        send_message("We have next overdue borrowings:")

        for borrowing in overdue_borrowings:
            message = (
                f"User {borrowing.user.full_name}\n"
                f"Book: {borrowing.book.title}\n"
                f"Expected return date was: {borrowing.expected_return_date}\n"
            )
            send_message(message)

    else:
        send_message("There is no overdue today!")
