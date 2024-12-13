import pytest
from django.contrib.auth.models import User
from rest_framework.test import APIClient

from EventsManager.EventsManager.models import Event

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def user_owner(db):
    return User.objects.create_user(username="testowner", email="test@example.com", password="password123")

@pytest.fixture
def user(db):
    return User.objects.create_user(username="testuser", email="other@example.com", password="password456")

@pytest.fixture
def event(db, user_owner):
    return Event.objects.create(
        title="Test Event",
        description="This is a test event",
        date="2024-12-31T12:00:00Z",
        location="Test Location",
        organizer=user_owner,
    )
