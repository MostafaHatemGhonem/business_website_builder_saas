from django.db import transaction
from django.utils import timezone
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from .models import Business, Membership 
from .permissions import IsBusinessOwner, IsBusinessManagerOrOwner, IsActiveBusinessMember
from .serializers import BusinessSerializer


class BusinessViewSet(viewsets.ModelViewSet):
    serializer_class = BusinessSerializer

    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return Business.objects.none()

        return Business.objects.filter(  
            memberships__user=self.request.user,
            memberships__status=Membership .Status.ACTIVE,
        ).distinct()

    def get_permissions(self):  
        if self.action == "destroy":
            return [IsAuthenticated(), IsBusinessOwner()]
        elif self.action in ["update", "partial_update"]:
            return [IsAuthenticated(), IsBusinessManagerOrOwner()]
        return [IsAuthenticated(), IsActiveBusinessMember()]

    def perform_create(self, serializer):
        """Automatically assigns the creator as an ACTIVE OWNER."""
        with transaction.atomic():
            business = serializer.save()
            Membership .objects.create(
                business=business,
                user=self.request.user,
                role=Membership .Role.OWNER,
                status=Membership .Status.ACTIVE,
                joined_at=timezone.now(),
            )
