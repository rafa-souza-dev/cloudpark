from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters import rest_framework as filters
from django.db.models import Q

from .models import Ticket, TicketStatus
from .serializers import TicketSerializer, TicketStatusUpdateSerializer
from authentication.models import UserProfile


class TicketFilter(filters.FilterSet):
    status = filters.ChoiceFilter(choices=TicketStatus.choices)
    priority = filters.ChoiceFilter(choices=Ticket.priority.field.choices)
    attendant = filters.NumberFilter(field_name='attendant__id')
    created_after = filters.DateTimeFilter(field_name='created_at', lookup_expr='gte')
    created_before = filters.DateTimeFilter(field_name='created_at', lookup_expr='lte')
    search = filters.CharFilter(method='search_filter')

    class Meta:
        model = Ticket
        fields = ['status', 'priority', 'attendant', 'created_after', 'created_before', 'search']

    def search_filter(self, queryset, name, value):
        return queryset.filter(
            Q(title__icontains=value) | Q(description__icontains=value)
        )


class TicketViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = TicketSerializer
    permission_classes = [IsAuthenticated]
    filterset_class = TicketFilter
    ordering_fields = ['created_at', 'updated_at', 'title', 'priority', 'status']
    ordering = ['-created_at']

    def get_queryset(self):
        user = self.request.user

        queryset = Ticket.objects.all()

        if user.is_superuser:
            return queryset
        elif hasattr(user, 'profile') and user.profile == UserProfile.TECHNICIAN:
            return queryset
        else:
            return queryset.filter(attendant=user)

    @action(detail=True, methods=['patch'], permission_classes=[IsAuthenticated])
    def update_status(self, request, pk=None):
        ticket = self.get_object()
        user = request.user

        if not self._can_update_status(user):
            return Response(
                {'error': 'Apenas técnicos podem alterar o status dos tickets.'},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = TicketStatusUpdateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        new_status = serializer.validated_data['status']

        if not self._is_valid_status_transition(ticket.status, new_status):
            return Response(
                {'error': 'Transição de status inválida.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        ticket.status = new_status
        ticket.save()

        return Response(TicketSerializer(ticket).data)

    def _can_update_status(self, user):
        return (
            user.is_superuser or 
            (hasattr(user, 'profile') and user.profile == UserProfile.TECHNICIAN)
        )

    def _is_valid_status_transition(self, current_status, new_status):
        valid_transitions = {
            TicketStatus.OPEN: [TicketStatus.IN_PROGRESS, TicketStatus.CANCELED],
            TicketStatus.IN_PROGRESS: [TicketStatus.RESOLVED, TicketStatus.CANCELED],
            TicketStatus.RESOLVED: [TicketStatus.IN_PROGRESS],
            TicketStatus.CANCELED: [TicketStatus.OPEN],
        }

        return new_status in valid_transitions.get(current_status, [])
