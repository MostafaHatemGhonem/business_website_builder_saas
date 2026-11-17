import uuid
from django.db import models
from django.db.models import F, Q
from django.core.validators import MinValueValidator
from apps.businesses.models import Business



class Plan(models.Model):
    class BillingInterval(models.TextChoices):
        MONTHLY = "Monthly", "monthly"
        YEARLY = "Yearly", "yearly"
        FREE = "Free", "free"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=50)
    code = models.SlugField(max_length=50, unique=True)
    description = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0)])
    currency = models.CharField(max_length=3, default="EGP")
    billing_interval = models.CharField(
        max_length=20,
        choices=BillingInterval.choices,
        default=BillingInterval.FREE
    )
    is_active = models.BooleanField(default=True)
    sort_order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        constraints = [
            models.CheckConstraint(condition=Q(price__gte=0), name="plan_price_nonnegative"),
        ]
    

class PlanFeature(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    plan_id = models.ForeignKey(
        Plan,
        null = False,
        blank= False,
        on_delete=models.CASCADE,
        related_name="plan_features",
    )
    key = models.CharField(max_length=100)
    value = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["plan_id", "key"], name="unique_plan_feature_key"),
        ]


class Subscription(models.Model):
    class Status(models.TextChoices):
        TRIALING = "Trialing",'trialing'
        ACTIVE = "Active", 'active'
        PAST_DUE = "Past_due", 'past_due'
        CANCELED = "Canceled", 'canceled'
        EXPIRED = "Expired", 'expired'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    business = models.ForeignKey(
        Business,
        null = False,
        blank= False,
        on_delete=models.PROTECT,
        related_name= 'business_subscription'        
    )
    plan_id = models.ForeignKey(
        Plan,
        null = False,
        blank= False,
        on_delete=models.PROTECT,
        related_name='business_plan'
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.TRIALING,
    )
    started_at = models.DateTimeField()
    current_period_start = models.DateTimeField()
    current_period_end = models.DateTimeField()
    trial_ends_at = models.DateTimeField(null=True, blank=True)
    canceled_at = models.DateTimeField(null=True, blank=True)
    cancel_at_period_end = models.BooleanField(default=False)
    provider = models.CharField(max_length=30, null=True, blank=True)
    provider_subscription_id = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=Q(current_period_end__gt=F("current_period_start")),
                name="subscription_period_end_after_start",
            ),
            models.UniqueConstraint(
                fields=["provider", "provider_subscription_id"],
                condition=Q(provider_subscription_id__isnull=False),
                name="unique_provider_subscription_reference",
            ),
        ]
        indexes = [
            models.Index(fields=["business", "status"]),
        ]



#! There Two conditional Models 
#? subscriptions_payment (conditional): Add if the SaaS collects subscription payments.
#? subscriptions_webhook_event (conditional): Track provider webhook processing.
