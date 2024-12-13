import pytest

from rest_framework import status

from EventsManager.EventsManager.models import Event

@pytest.mark.django_db
def test_create_event(api_client, user_owner, user):
    api_client.force_authenticate(user=user_owner)
    data = {
        "title": "New Event",
        "description": "A new test event",
        "date": "2024-12-31T15:00:00Z",
        "location": "New Location",
        "invitees": [user.email]
    }
    response = api_client.post("/api/events/", data, format="json")
    assert response.status_code == status.HTTP_201_CREATED
    assert Event.objects.count() == 1
    event = Event.objects.last()
    assert event.attendees.count() == 1

@pytest.mark.django_db
def test_list_events(api_client, user_owner, event):
    api_client.force_authenticate(user=user_owner)
    response = api_client.get("/api/events/")
    assert response.status_code == status.HTTP_200_OK
    assert response.data["count"] == 1

@pytest.mark.django_db
def test_retrieve_event(api_client, user_owner, event):
    api_client.force_authenticate(user=user_owner)
    response = api_client.get(f"/api/events/{event.id}/")
    assert response.status_code == status.HTTP_200_OK
    assert response.data["title"] == event.title

@pytest.mark.django_db
def test_update_event(api_client, user_owner, event):
    api_client.force_authenticate(user=user_owner)
    data = {"title": "Updated Event Title"}
    response = api_client.patch(f"/api/events/{event.id}/", data, format="json")
    assert response.status_code == status.HTTP_200_OK
    event.refresh_from_db()
    assert event.title == "Updated Event Title"

def test_event_register(api_client, event, user):
    api_client.force_authenticate(user=user)
    url = f'/api/events/{event.id}/register/'
    response = api_client.post(url)
    assert response.status_code == 200
    assert response.data['status'] == 'registered'
    assert user in event.attendees.all()

def test_event_invited(api_client, event, user):
    api_client.force_authenticate(user=user)
    url = '/api/events/'
    response = api_client.get(url)
    assert response.status_code == 200
    assert response.data["count"] == 1

    response = api_client.get(url, {"invited": "true"})
    assert response.status_code == 200
    assert response.data["count"] == 0

def test_event_tittle_filter(api_client, event, user_owner):
    api_client.force_authenticate(user=user_owner)
    url = '/api/events/'
    response = api_client.get(url, {"title": "Test"})
    assert response.status_code == 200
    assert response.data["count"] == 1

    response = api_client.get(url, {"title": "Not exist event"})
    assert response.status_code == 200
    assert response.data["count"] == 0

@pytest.mark.django_db
def test_event_permissions(api_client, event, user):
    api_client.force_authenticate(user=user)
    data = {"title": "Updated Event Title"}
    response = api_client.patch(f"/api/events/{event.id}/", data, format="json")
    assert response.status_code == status.HTTP_403_FORBIDDEN
