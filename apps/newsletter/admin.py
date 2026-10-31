import csv
from django.contrib import admin
from django.http import HttpResponse
from django.utils import timezone
from unfold.admin import ModelAdmin
from unfold.decorators import action, display

from .models import NewsletterSubscriber


@admin.register(NewsletterSubscriber)
class NewsletterSubscriberAdmin(ModelAdmin):
    list_display = (
        'email',
        'display_confirmed',
        'display_active',
        'created_at',
        'confirmed_at',
        'unsubscribed_at',
    )
    list_filter = ('is_active', 'is_confirmed', 'created_at')
    search_fields = ('email',)
    date_hierarchy = 'created_at'
    actions = ['export_as_csv', 'mark_as_confirmed', 'unsubscribe_selected']

    @display(description="Confirmed", boolean=True)
    def display_confirmed(self, obj):
        return obj.is_confirmed

    @display(description="Active", boolean=True)
    def display_active(self, obj):
        return obj.is_active

    @action(description="Export selected subscribers to CSV")
    def export_as_csv(self, request, queryset):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="subscribers_{timezone.now().strftime("%Y%m%d_%H%M%S")}.csv"'
        writer = csv.writer(response)
        writer.writerow(['Email', 'Confirmed', 'Active', 'Created At', 'Confirmed At', 'Unsubscribed At'])
        for sub in queryset:
            writer.writerow([
                sub.email,
                sub.is_confirmed,
                sub.is_active,
                sub.created_at.strftime('%Y-%m-%d %H:%M:%S') if sub.created_at else '',
                sub.confirmed_at.strftime('%Y-%m-%d %H:%M:%S') if sub.confirmed_at else '',
                sub.unsubscribed_at.strftime('%Y-%m-%d %H:%M:%S') if sub.unsubscribed_at else '',
            ])
        return response

    @action(description="Mark selected subscribers as confirmed")
    def mark_as_confirmed(self, request, queryset):
        count = queryset.update(is_confirmed=True, confirmed_at=timezone.now())
        self.message_user(request, f"{count} subscriber(s) marked as confirmed.")

    @action(description="Unsubscribe selected users")
    def unsubscribe_selected(self, request, queryset):
        count = queryset.update(is_active=False, unsubscribed_at=timezone.now())
        self.message_user(request, f"{count} subscriber(s) unsubscribed.")
