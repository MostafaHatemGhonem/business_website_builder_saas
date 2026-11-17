from django.contrib import admin

from .models import Plan, PlanFeature, Subscription


@admin.register(Plan)
class PlanAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "price", "currency", "billing_interval", "is_active", "sort_order")
    list_filter = ("billing_interval", "currency", "is_active")
    search_fields = ("name", "code")
    readonly_fields = ("created_at", "updated_at")


@admin.register(PlanFeature)
class PlanFeatureAdmin(admin.ModelAdmin):
    list_display = ("plan_id", "key", "value", "created_at")
    search_fields = ("plan_id__name", "key")
    readonly_fields = ("created_at", "updated_at")


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ("business", "plan_id", "status", "provider", "current_period_end")
    list_filter = ("status", "provider")
    search_fields = ("business__name", "provider_subscription_id")
    readonly_fields = ("created_at", "updated_at")
