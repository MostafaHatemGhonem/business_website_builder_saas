from django.conf import settings
from apps.orders.models import Order
from apps.businesses.models import Business
import uuid
from django.db import models


class WhatsappIntegration(models.Model):
    class Mode(models.TextChoices):
        PROVIDER = 'Provider', 'provider'
        SPECIFIC_MODE = 'Specific_mode', 'specific_mode'

    class Status(models.TextChoices):
        PENDING = 'Pending', 'pending'
        CONNECTED = 'Connected', 'connected'
        ERROR = 'Error', "error"
        DISCONNECTED = 'Disconnected', 'disconnected'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    business = models.OneToOneField(
        Business,
        unique=True,
        null=False,
        blank=False,
        on_delete=models.CASCADE,
        related_name='business_whatsapp'
    )
    mode = models.CharField(
        max_length=20,
        choices=Mode.choices,
        default=Mode.PROVIDER
    )
    phone_number = models.CharField(max_length=30)
    provider = models.CharField(max_length=30)
    provider_phone_number_id = models.CharField(max_length=255, null=True, blank=True)
    provider_business_account_id = models.CharField(max_length=255, null=True, blank=True)
    credentials_secret_ref = models.CharField(max_length=255, null=True, blank=True)
    is_enabled = models.BooleanField(default=False)
    connected_at = models.DateTimeField(null=True, blank=True)
    connection_status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING
    )
    last_error = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True) 



class NotificationOutBox(models.Model):
    class Status(models.TextChoices):
        PENDING = 'Pending', 'pending'
        PROCESSING = 'Processing', 'processing'
        COMPLETED = 'Completed', 'completed'
        FAILED = 'Failed', 'failed'
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    business = models.ForeignKey(
        Business,
        null=False,
        blank=False,
        on_delete=models.PROTECT,
        related_name='business_notification'
    )
    order = models.ForeignKey(
        Order,
        null=False,
        blank=False,
        on_delete=models.PROTECT,
        related_name='notification_outbox_entries'
    )
    event_type = models.CharField(max_length=50)
    payload = models.JSONField()
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING
    )
    attempt_count = models.PositiveIntegerField(default=0)
    next_attempt_at = models.DateTimeField(null=True, blank=True)
    deduplication_key = models.CharField(max_length=150, unique=True)
    last_error = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class NotificationLog(models.Model):
    class Status(models.TextChoices):
        QUEUED = 'Queued', 'queued'
        SENT = 'Sent', "sent"
        DELIVERED = 'Delivered', 'delivered'
        FAILED = 'Failed', 'failed'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    business = models.ForeignKey(
        Business,
        null=False,
        blank=False,
        on_delete=models.CASCADE,
        related_name='business_notification_log'
    )
    order = models.ForeignKey(
        Order,
        null=False,
        blank=False,
        on_delete=models.CASCADE,
        related_name='notification_logs'
    )
    channel = models.CharField(max_length=20)
    event_type = models.CharField(max_length=50)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.QUEUED    
    )
    provider_message_id = models.CharField(max_length=255, null=True, blank=True)
    attempt_count = models.PositiveIntegerField(default=0)
    next_retry_at = models.DateTimeField( null=True, blank=True)
    last_error = models.TextField( null=True, blank=True)
    sent_at = models.DateTimeField( null=True, blank=True)
    delivered_at = models.DateTimeField( null=True, blank=True)
    deduplication_key = models.CharField(max_length=150, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class AuditLog(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    business = models.ForeignKey(
        Business,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='business_audit_log'
    )
    actor_user_id = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True, 
        blank=True,
        on_delete=models.SET_NULL,
        related_name='user_audit_log'
    )
    action = models.CharField(max_length=100)
    target_type = models.CharField(max_length=100, null=True, blank=True)
    target_id = models.CharField(max_length=100, null=True, blank=True)
    metadata = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)




    