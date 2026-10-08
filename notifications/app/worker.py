from celery import Celery

from app.config import settings
from app.emailer import EmailMessage, EmailProvider

celery_app = Celery("notebook_notifications", broker=settings.redis_url, backend=settings.redis_url)
celery_app.conf.beat_schedule = {
    "scan-due-reminders-every-minute": {
        "task": "app.worker.scan_due_reminders",
        "schedule": 60.0,
    }
}


@celery_app.task
def send_note_shared_email(email: str, note_title: str) -> str:
    EmailProvider().send(EmailMessage(to=email, subject="A note was shared with you", body=f"Open: {note_title}"))
    return "sent"


@celery_app.task
def scan_due_reminders() -> str:
    return "reminder_scan_stubbed"
