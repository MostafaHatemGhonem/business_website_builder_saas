from django.contrib import admin

from .models import Business, BusinessHours, Membership


@admin.register(Business)
class BusinessAdmin(admin.ModelAdmin):
    list_display = ("name", "business_type", "slug", "currency", "is_active", "created_at")
    list_filter = ("business_type", "currency", "is_active")
    search_fields = ("name", "slug", "email", "phone")
    readonly_fields = ("created_at", "updated_at")


@admin.register(Membership)
class MembershipAdmin(admin.ModelAdmin):
    list_display = ("business", "user", "role", "status", "joined_at")
    list_filter = ("role", "status")
    search_fields = ("business__name", "user__email")
    readonly_fields = ("created_at", "updated_at")


@admin.register(BusinessHours)
class BusinessHoursAdmin(admin.ModelAdmin):
    list_display = ("business", "weekday", "opens_at", "closes_at", "is_closed")
    list_filter = ("weekday", "is_closed")
    search_fields = ("business__name",)
    readonly_fields = ("created_at", "updated_at")
