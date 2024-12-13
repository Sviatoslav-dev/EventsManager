import pytest
from django.contrib.auth.models import User

from EventsManager.EventsManager.models import Event


@pytest.mark.django_db
def test_event_creation():
    user = User.objects.create_user(username="testuser", email="test@example.com", password="password123")
    event = Event.objects.create(
        title="Test Event",
        description="This is a test event.",
        date="2024-12-31T12:00:00Z",
        location="Test Location",
        organizer=user,
    )
    assert event.title == "Test Event"
    assert event.organizer == user
    assert event.attendees.count() == 0
