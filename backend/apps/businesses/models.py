import uuid
from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator



class Business(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=150, unique=True)
    business_type = models.CharField(max_length=30)
    description = models.TextField(blank=True)
    logo = models.URLField(blank=True, null=True)
    phone = models.CharField(max_length=30, blank=True, null=True)
    email = models.EmailField(blank=True,null=True)
    address = models.JSONField(blank=True,null=True)
    currency = models.CharField(max_length=3, default="EGP")
    timezone = models.CharField(max_length=50, default="Africa/Cairo")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} in {self.business_type}"

    def get_user_role(self, user):
        """
        Helper to get user's role in this business.
        """
        membership = self.memberships.filter(user=user,
        status=Membership.Status.ACTIVE).first()
        return membership.role if membership else None



class Membership(models.Model):
    
    class Role(models.TextChoices):
        OWNER = "owner", "Owner"
        MANAGER = "manager", "Manager"
        STAFF = "staff", "Staff"
    
    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        INVITED = "invited", "Invited"
        SUSPENDED = "suspended", "Suspended"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    business = models.ForeignKey(
        Business,
        on_delete=models.CASCADE,
        # blank=False,
        # null=False,
        related_name="memberships",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        # blank=False,
        # null=False,
        related_name="business_memberships",
    )
    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.STAFF
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.INVITED
    )
    invited_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="sent_business_invitations",
    )

    joined_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['business', 'user'],
                name="unique_business_membership"
            )
        ]
        indexes = [
            models.Index(fields=["business", "status", "role"]),
        ]

    def __str__(self):
        return f"{self.user} in {self.business.name} ({self.role})"



class BusinessHours(models.Model):
    class Weekday(models.IntegerChoices):
        MONDAY = 0, "Monday"
        TUESDAY = 1, "Tuesday"
        WEDNESDAY = 2, "Wednesday"
        THURSDAY = 3, "Thursday"
        FRIDAY = 4, "Friday"
        SATURDAY = 5, "Saturday"
        SUNDAY = 6, "Sunday"
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    business = models.ForeignKey(
        Business,
        null=False,
        blank=False,
        on_delete=models.CASCADE,
        related_name='business_hours'
    )
    weekday = models.PositiveSmallIntegerField(
        choices=Weekday.choices,
        validators =[
            MinValueValidator(0),
            MaxValueValidator(6),
        ]
    )
    opens_at = models.TimeField(null=True, blank=True)
    closes_at = models.TimeField(null=True, blank=True)
    is_closed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["business", "weekday"],
                name="unique_business_hours_weekday",
            ),
        ]
    