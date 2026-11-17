import uuid
from django.db import models
from django.db.models import Q
from django.core.validators import MinValueValidator
from apps.businesses.models import Business


class Category(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    business = models.ForeignKey(
        Business,
        null = False,
        blank= False,
        on_delete=models.CASCADE,
        related_name='categories'
    )
    name = models.CharField(max_length=120)
    slug = models.SlugField(max_length=140,unique=True)
    description = models.TextField(null=True,blank=True)
    position = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["business", "slug"], name="unique_category_slug_per_business"),
        ]

class Product(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    business = models.ForeignKey(
        Business,
        null = False,
        blank= False,
        on_delete=models.CASCADE,
        related_name='products'
    )
    category_id = models.ForeignKey(
        Category,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='products'
    )
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200)
    description = models.TextField(null=True, blank=True)
    price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(0)],
    )
    currency = models.CharField(max_length=3, default="EGP")
    image = models.URLField(null=True, blank=True)
    is_available = models.BooleanField(default=True)
    position = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["business", "slug"], name="unique_product_slug_per_business"),
            models.CheckConstraint(condition=Q(price__gte=0), name="product_price_nonnegative"),
        ]


class ProductVariant(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    product_id = models.ForeignKey(
        Product,
        null = False,
        blank= False,
        on_delete=models.CASCADE,
        related_name='product_variant'
    )
    name = models.CharField(max_length=100)
    sku = models.CharField(max_length=100, null=True, blank=True)
    price_delta = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    is_available = models.BooleanField(default=True)
    position = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["product_id", "sku"],
                condition=Q(sku__isnull=False),
                name="unique_variant_sku_per_product",
            ),
        ]


#! There something conditional models.models
#? catalog_optiongroup (conditional): For add-ons and required selections.
#? catalog_option (conditional): Option within group.
#? catalog_product_optiongroup (conditional): Through model if product-option groups are many-to-many.
