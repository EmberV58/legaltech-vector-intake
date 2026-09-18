from datetime import date, timedelta

from src.legal_pipeline import deadline_follow_up


def test_deadline_equal_to_today_is_due() -> None:
    today = date(2026, 9, 2)
    assert deadline_follow_up(today, today) == "due"
    assert deadline_follow_up(today + timedelta(days=1), today) == "scheduled"

