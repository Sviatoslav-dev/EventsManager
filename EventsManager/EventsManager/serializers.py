from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Event

class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = ['id', 'title', 'description', 'date', 'location', 'organizer', 'attendees']
        read_only_fields = ['organizer', 'attendees']

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']
