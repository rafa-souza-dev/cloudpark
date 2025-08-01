from django.contrib import admin
from django.contrib import messages

from .models import Ticket, TicketStatus


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ['title', 'priority', 'status', 'attendant', 'created_at']
    list_filter = ['priority', 'status', 'created_at']
    search_fields = ['title', 'description']
    readonly_fields = ['attendant', 'created_at', 'updated_at']

    fieldsets = (
        ('Informações Básicas', {
            'fields': ('title', 'priority', 'status', 'description')
        }),
        ('Informações do Sistema', {
            'fields': ('attendant', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def get_fieldsets(self, request, obj=None):
        fieldsets = super().get_fieldsets(request, obj)
        if obj is None:
            basic_fields = list(fieldsets[0][1]['fields'])
            if 'attendant' in basic_fields:
                basic_fields.remove('attendant')
            fieldsets = (
                ('Informações Básicas', {
                    'fields': tuple(basic_fields)
                }),
                ('Informações do Sistema', {
                    'fields': ('created_at', 'updated_at'),
                    'classes': ('collapse',)
                }),
            )
        return fieldsets

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)

        if obj and request.user.profile == 'attendant':
            status_field = form.base_fields.get('status')
            if status_field:
                choices = list(status_field.choices)
                choices = [choice for choice in choices if choice[0] != TicketStatus.RESOLVED]
                status_field.choices = choices

        return form

    def save_model(self, request, obj, form, change):
        if not change:
            obj.attendant = request.user
        else:
            if request.user.profile == 'attendant':
                if obj.status == TicketStatus.RESOLVED:
                    original_obj = Ticket.objects.get(pk=obj.pk)
                    if original_obj.status != TicketStatus.RESOLVED:
                        messages.error(request, 'Usuários com perfil de atendente não podem alterar o status para "Resolvido".')
                        return

        super().save_model(request, obj, form, change)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(attendant=request.user)

    def has_add_permission(self, request):
        return request.user and request.user.is_authenticated

    def has_change_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        if obj is None:
            return True
        return obj.attendant == request.user

    def has_delete_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        if obj is None:
            return False
        return obj.attendant == request.user
