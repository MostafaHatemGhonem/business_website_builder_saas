from apps.businesses.models import Business
import uuid
from django.db import models
from django.db.models import Q


class Theme(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    preview_image = models.URLField(null=True, blank=True)
    schema_version = models.PositiveIntegerField(default=1)
    default_config = models.JSONField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Website(models.Model):
    class Status(models.TextChoices):
        DRAFT = 'Draft', 'draft'
        PUBLISHED = 'Published', 'published'
        SUSPENDED = 'Suspended', 'suspended'
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    business = models.OneToOneField(
        Business,
        null = False,
        blank= False,
        related_name="business_website",
        on_delete=models.PROTECT,
        unique=True,
    )
    theme_id = models.ForeignKey(
        Theme,
        null = False,
        blank= False,
        on_delete=models.PROTECT,
        related_name='website_theme'
    )
    slug = models.SlugField(max_length=150)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.DRAFT
    )
    site_config = models.JSONField()
    published_version = models.PositiveIntegerField(default=0)
    published_config = models.JSONField(null=True, blank=True)
    published_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class WebsiteSection(models.Model):
    class Type(models.TextChoices):
        HERO = "Hero", "hero"
        PRODUCT_GRID = "Product_gird", "product_grid"
        GALLERY = "Gallery", "gallery"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    website_id = models.ForeignKey(
        Website,
        null=False,
        blank=False,
        on_delete=models.CASCADE,
        related_name='website_section'
    )
    type = models.CharField(
        max_length=50,
        choices=Type.choices,
        default=Type.HERO
    )
    position = models.PositiveIntegerField(default=0)
    is_visible = models.BooleanField(default=True)
    settings = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=["website_id", "position"]),
        ]


class Domain(models.Model):
    class Status(models.TextChoices):
        PENDING = 'Pending', 'pending'
        VERIFIED = 'Verified', 'verified'
        FAILED = 'Failed', 'failed'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    website_id = models.ForeignKey(
        Website,
        null = False,
        blank= False,
        on_delete=models.CASCADE,
        related_name='website_domain'
    )
    hostname = models.CharField(max_length=253, unique=True)
    domain_type = models.CharField(
        max_length=20,
        choices=[("platform", "Platform"), ("custom", "Custom")],
    )
    is_primary = models.BooleanField(default=False)
    verification_status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING
    ) 
    verified_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["website_id"],
                condition=Q(is_primary=True),
                name="unique_primary_domain_per_website",
            ),
        ]
