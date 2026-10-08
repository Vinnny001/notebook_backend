from app.worker import scan_due_reminders


def test_scan_due_reminders_stub() -> None:
    assert scan_due_reminders.run() == "reminder_scan_stubbed"
