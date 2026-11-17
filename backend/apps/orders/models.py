from apps.businesses.models import Business
from apps.catalog.models import Product, ProductVariant
import uuid
from django.db import models
from django.core.exceptions import ValidationError
from django.conf import settings
from django.db.models import Q


def validate_positive(value):
    if value < 0:
        raise ValidationError("Value must be zero or greater.")
    

def validate_one(value):
    if value < 1:
        raise ValidationError("Value must be at least one.")
    



class Customer(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    business = models.ForeignKey(
        Business,
        null=False,
        blank=False,
        on_delete=models.PROTECT,
        related_name='business_customer'
    )
    name = models.CharField(max_length=200)
    phone = models.CharField(max_length=30)
    email = models.EmailField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=["business", "phone"]),
        ]



class Order(models.Model):
    class Status(models.TextChoices):
        PENDING = 'Pending', 'pending'
        CONFIRMED = 'Confirmed', 'confirmed'
        PREPARING = 'Preparing', 'preparing'
        READY = 'Ready', 'ready'
        COMPLETED = 'Completed', 'completed'
        CANCELLED = 'Cancelled', 'cancelled'

    class Channel(models.TextChoices):
        WEBSITE = "Website", "website"
        ADMIN = "Admin", "admin"

    class Delivery(models.TextChoices):
        PICKUP = "Pickup", 'pickup'
        DELIVERY = 'Delivery', 'delivery'


    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    business = models.ForeignKey(
        Business,
        null=False,
        blank=False,
        on_delete=models.CASCADE,
        related_name='business_orders'
    )
    customer_id = models.ForeignKey(
        Customer,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='customer_order'
    )
    order_number = models.CharField(max_length=40)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING
    )
    channel = models.CharField(
        max_length=20,
        choices=Channel.choices,
        default=Channel.WEBSITE
    )
    customer_name =models.CharField(max_length=200)
    customer_phone = models.CharField(max_length=30)
    delivery_type = models.CharField(
        max_length=20,
        choices=Delivery.choices,
        default=Delivery.DELIVERY
    )
    delivery_address = models.JSONField(null=True, blank=True)
    customer_notes = models.TextField(null=True, blank=True)
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, validators=[validate_positive])
    delivery_fee = models.DecimalField(max_digits=12, decimal_places=2, validators=[validate_positive])
    discount_amount = models.DecimalField(max_digits=12, decimal_places=2, validators=[validate_positive])
    total = models.DecimalField(max_digits=12, decimal_places=2, validators=[validate_positive])
    currency = models.CharField(max_length=3, default="EGP")
    idempotency_key = models.CharField(max_length=100, null=True, blank=True)
    placed_at = models.DateTimeField()
    confirmed_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["business", "idempotency_key"],
                condition=Q(idempotency_key__isnull=False),
                name="unique_order_idempotency_key_per_business",
            ),
            models.UniqueConstraint(
                fields=["business", "order_number"],
                name="unique_order_number_per_business",
            ),
            models.CheckConstraint(condition=Q(subtotal__gte=0), name="order_subtotal_nonnegative"),
            models.CheckConstraint(condition=Q(delivery_fee__gte=0), name="order_delivery_fee_nonnegative"),
            models.CheckConstraint(condition=Q(discount_amount__gte=0), name="order_discount_nonnegative"),
            models.CheckConstraint(condition=Q(total__gte=0), name="order_total_nonnegative"),
        ]
        indexes = [
            models.Index(fields=["business", "status", "created_at"]),
        ]



class OrderItem(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order = models.ForeignKey(
        Order,
        null = False,
        blank= False,
        on_delete=models.CASCADE,
        related_name="order_item"    
    )
    product_id = models.ForeignKey(
        Product,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='product_order_item'
    )
    variant_id = models.ForeignKey(
        ProductVariant,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='variant_order_item'
    )
    product_name = models.CharField(max_length=200)
    variant_name = models.CharField(max_length=100, null=True, blank=True)
    sku = models.CharField(max_length=100, null=True, blank=True)
    quantity = models.PositiveIntegerField(validators=[validate_one])
    unit_price = models.DecimalField(max_digits=12, decimal_places=2)
    line_total = models.DecimalField(max_digits=12, decimal_places=2)
    selected_options = models.JSONField(default=list)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.CheckConstraint(condition=Q(quantity__gte=1), name="order_item_quantity_positive"),
            models.CheckConstraint(condition=Q(unit_price__gte=0), name="order_item_unit_price_nonnegative"),
            models.CheckConstraint(condition=Q(line_total__gte=0), name="order_item_line_total_nonnegative"),
        ]


class OrderStatusHistory(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order = models.ForeignKey(
        Order,
        null=False,
        blank=False,
        on_delete=models.CASCADE,
        related_name='order_status_history'
    )
    old_status = models.CharField(max_length=20, null=True, blank=True)
    new_status = models.CharField(max_length=20)
    changed_by_id = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='user_order_status_history'
    )
    note = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=["order", "created_at"]),
        ]
