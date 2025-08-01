from rest_framework import serializers
from authentication.models import User

from .models import Ticket, TicketStatus


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'profile']


class TicketSerializer(serializers.ModelSerializer):
    attendant = UserSerializer(read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    priority_display = serializers.CharField(source='get_priority_display', read_only=True)

    class Meta:
        model = Ticket
        fields = [
            'id', 'title', 'description', 'priority', 'priority_display',
            'status', 'status_display', 'attendant', 'created_at', 'updated_at'
        ]
        read_only_fields = ['attendant', 'created_at', 'updated_at']


class TicketStatusUpdateSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=TicketStatus.choices)
