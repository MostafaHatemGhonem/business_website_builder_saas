from types import SimpleNamespace

from django.contrib.auth import get_user_model
from django.test import SimpleTestCase, TestCase
from rest_framework.permissions import IsAuthenticated
from rest_framework.test import APIRequestFactory

from .models import Business, Membership
from .permissions import (
    IsActiveBusinessMember,
    IsBusinessManagerOrOwner,
    IsBusinessOwner,
)
from .serializers import BusinessSerializer
from .views import BusinessViewSet

User = get_user_model()


class BusinessViewSetPermissionUnitTests(SimpleTestCase):
    def test_get_permissions_by_action(self):
        cases = {
            "list": [IsAuthenticated],
            "create": [IsAuthenticated],
            "retrieve": [IsAuthenticated, IsActiveBusinessMember],
            "update": [IsAuthenticated, IsBusinessManagerOrOwner],
            "partial_update": [IsAuthenticated, IsBusinessManagerOrOwner],
            "destroy": [IsAuthenticated, IsBusinessOwner],
        }
        for action, expected_types in cases.items():
            view = BusinessViewSet()
            view.action = action
            perms = view.get_permissions()
            self.assertEqual([type(p) for p in perms], expected_types, msg=f"action={action}")


class BusinessTenantIsolationTests(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.owner = User.objects.create_user(email="owner@example.com", password="StrongPassword!234")
        self.manager = User.objects.create_user(email="manager@example.com", password="StrongPassword!234")
        self.outsider = User.objects.create_user(email="outsider@example.com", password="StrongPassword!234")
        self.staff = User.objects.create_user(email="staff@example.com", password="StrongPassword!234")
        self.suspended_member = User.objects.create_user(
            email="suspended@example.com", password="StrongPassword!234"
        )

        self.business = Business.objects.create(
            name="Cairo Cafe",
            slug="cairo-cafe",
            business_type="cafe",
        )
        Membership.objects.create(
            business=self.business,
            user=self.owner,
            role=Membership.Role.OWNER,
            status=Membership.Status.ACTIVE,
        )
        Membership.objects.create(
            business=self.business,
            user=self.manager,
            role=Membership.Role.MANAGER,
            status=Membership.Status.ACTIVE,
        )
        Membership.objects.create(
            business=self.business,
            user=self.staff,
            role=Membership.Role.STAFF,
            status=Membership.Status.ACTIVE,
        )
        Membership.objects.create(
            business=self.business,
            user=self.suspended_member,
            role=Membership.Role.OWNER,
            status=Membership.Status.SUSPENDED,
        )

    def test_queryset_excludes_non_members(self):
        request = self.factory.get("/businesses/")
        request.user = self.outsider
        view = BusinessViewSet()
        view.request = request
        self.assertFalse(view.get_queryset().filter(pk=self.business.pk).exists())

    def test_object_permissions_block_cross_tenant_and_enforce_roles(self):
        request = SimpleNamespace(user=self.outsider)
        self.assertFalse(IsActiveBusinessMember().has_object_permission(request, None, self.business))
        self.assertFalse(IsBusinessManagerOrOwner().has_object_permission(request, None, self.business))
        self.assertFalse(IsBusinessOwner().has_object_permission(request, None, self.business))

        staff_request = SimpleNamespace(user=self.staff)
        self.assertTrue(IsActiveBusinessMember().has_object_permission(staff_request, None, self.business))
        self.assertFalse(IsBusinessManagerOrOwner().has_object_permission(staff_request, None, self.business))
        self.assertFalse(IsBusinessOwner().has_object_permission(staff_request, None, self.business))

        owner_request = SimpleNamespace(user=self.owner)
        self.assertTrue(IsBusinessOwner().has_object_permission(owner_request, None, self.business))

    def test_manager_can_update_but_cannot_delete_business(self):
        manager_request = SimpleNamespace(user=self.manager)
        view = BusinessViewSet()

        for action in ("update", "partial_update"):
            view.action = action
            perms = view.get_permissions()
            self.assertTrue(any(isinstance(p, IsBusinessManagerOrOwner) for p in perms))
            self.assertTrue(
                all(p.has_object_permission(manager_request, view, self.business) for p in perms)
            )

        view.action = "destroy"
        destroy_perms = view.get_permissions()
        self.assertTrue(any(isinstance(p, IsBusinessOwner) for p in destroy_perms))
        self.assertFalse(
            all(p.has_object_permission(manager_request, view, self.business) for p in destroy_perms)
        )

    def test_suspended_membership_cannot_access_business(self):
        request = self.factory.get("/businesses/")
        request.user = self.suspended_member
        view = BusinessViewSet()
        view.request = request
        self.assertFalse(view.get_queryset().filter(pk=self.business.pk).exists())

        perm_request = SimpleNamespace(user=self.suspended_member)
        self.assertFalse(IsActiveBusinessMember().has_object_permission(perm_request, None, self.business))
        self.assertFalse(IsBusinessManagerOrOwner().has_object_permission(perm_request, None, self.business))
        self.assertFalse(IsBusinessOwner().has_object_permission(perm_request, None, self.business))

    def test_perform_create_creates_business_and_active_owner_membership(self):
        request = self.factory.post("/businesses/")
        request.user = self.outsider
        view = BusinessViewSet()
        view.request = request

        serializer = BusinessSerializer(
            data={
                "name": "Alex Bakery",
                "slug": "alex-bakery",
                "business_type": "bakery",
            }
        )
        self.assertTrue(serializer.is_valid(), serializer.errors)
        view.perform_create(serializer)

        created_business = Business.objects.get(slug="alex-bakery")
        membership = Membership.objects.get(business=created_business, user=self.outsider)
        self.assertEqual(membership.user, self.outsider)
        self.assertEqual(membership.role, Membership.Role.OWNER)
        self.assertEqual(membership.status, Membership.Status.ACTIVE)
        self.assertIsNotNone(membership.joined_at)
