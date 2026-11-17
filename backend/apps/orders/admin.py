from django.contrib import admin

from .models import Customer, Order, OrderItem, OrderStatusHistory


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ("created_at",)


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ("name", "business", "phone", "email", "created_at")
    search_fields = ("name", "phone", "email", "business__name")
    readonly_fields = ("created_at", "updated_at")


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("order_number", "business", "customer_name", "status", "channel", "total", "placed_at")
    list_filter = ("status", "channel", "delivery_type", "currency")
    search_fields = ("order_number", "customer_name", "customer_phone", "business__name")
    readonly_fields = ("created_at", "updated_at")
    inlines = (OrderItemInline,)


@admin.register(OrderStatusHistory)
class OrderStatusHistoryAdmin(admin.ModelAdmin):
    list_display = ("order", "old_status", "new_status", "changed_by_id", "created_at")
    list_filter = ("old_status", "new_status")
    search_fields = ("order__order_number", "note")
    readonly_fields = ("created_at",)
