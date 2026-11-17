from django.contrib import admin

from .models import AuditLog, NotificationLog, NotificationOutBox, WhatsappIntegration


@admin.register(WhatsappIntegration)
class WhatsappIntegrationAdmin(admin.ModelAdmin):
    list_display = ("business", "provider", "is_enabled", "connection_status", "connected_at")
    list_filter = ("provider", "is_enabled", "connection_status")
    search_fields = ("business__name", "phone_number", "provider")
    readonly_fields = ("created_at", "updated_at")


@admin.register(NotificationOutBox)
class NotificationOutBoxAdmin(admin.ModelAdmin):
    list_display = ("business", "order", "event_type", "status", "attempt_count", "next_attempt_at")
    list_filter = ("status", "event_type")
    search_fields = ("business__name", "order__order_number", "deduplication_key")
    readonly_fields = ("created_at", "updated_at")


@admin.register(NotificationLog)
class NotificationLogAdmin(admin.ModelAdmin):
    list_display = ("business", "order", "channel", "event_type", "status", "sent_at", "delivered_at")
    list_filter = ("channel", "event_type", "status")
    search_fields = ("business__name", "order__order_number", "provider_message_id")
    readonly_fields = ("created_at", "updated_at")


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ("business", "action", "target_type", "target_id", "created_at")
    list_filter = ("action", "target_type")
    search_fields = ("business__name", "action", "target_type", "target_id")
    readonly_fields = ("created_at",)
