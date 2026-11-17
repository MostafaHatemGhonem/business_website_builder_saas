from django.contrib import admin

from .models import Category, Product, ProductVariant


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "business", "slug", "position", "is_active")
    list_filter = ("is_active",)
    search_fields = ("name", "slug", "business__name")
    readonly_fields = ("created_at", "updated_at")


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "business", "category_id", "price", "is_available", "position")
    list_filter = ("is_available", "currency")
    search_fields = ("name", "slug", "business__name")
    readonly_fields = ("created_at", "updated_at")


@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):
    list_display = ("name", "product_id", "sku", "price_delta", "is_available", "position")
    list_filter = ("is_available",)
    search_fields = ("name", "sku", "product_id__name")
    readonly_fields = ("created_at", "updated_at")
