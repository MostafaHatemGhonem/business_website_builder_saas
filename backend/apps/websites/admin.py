from django.contrib import admin

from .models import Domain, Theme, Website, WebsiteSection


@admin.register(Theme)
class ThemeAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "schema_version", "is_active", "created_at")
    list_filter = ("is_active", "schema_version")
    search_fields = ("name", "slug")
    readonly_fields = ("created_at", "updated_at")


@admin.register(Website)
class WebsiteAdmin(admin.ModelAdmin):
    list_display = ("business", "slug", "status", "theme_id", "published_at")
    list_filter = ("status",)
    search_fields = ("business__name", "slug")
    readonly_fields = ("created_at", "updated_at")


@admin.register(WebsiteSection)
class WebsiteSectionAdmin(admin.ModelAdmin):
    list_display = ("website_id", "type", "position", "is_visible")
    list_filter = ("type", "is_visible")
    search_fields = ("website_id__slug",)
    readonly_fields = ("created_at", "updated_at")


@admin.register(Domain)
class DomainAdmin(admin.ModelAdmin):
    list_display = ("hostname", "website_id", "domain_type", "is_primary", "verification_status")
    list_filter = ("domain_type", "is_primary", "verification_status")
    search_fields = ("hostname", "website_id__slug")
    readonly_fields = ("created_at", "updated_at")
