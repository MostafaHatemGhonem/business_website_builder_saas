from rest_framework import permissions

from .models import Business, Membership


def get_object_business(obj):
    if isinstance(obj, Business):
        return obj

    return getattr(obj, "business", None)


def get_active_membership(user, business):
    if not user.is_authenticated or business is None:
        return None

    return Membership.objects.filter(
        user=user,
        business=business,
        status=Membership.Status.ACTIVE,
    ).first()


class IsActiveBusinessMember(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        business = get_object_business(obj)

        return get_active_membership(
            request.user,
            business,
        ) is not None


class IsBusinessManagerOrOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        membership = get_active_membership(
            request.user,
            get_object_business(obj),
        )

        return membership is not None and membership.role in {
            Membership.Role.OWNER,
            Membership.Role.MANAGER,
        }


class IsBusinessOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        membership = get_active_membership(
            request.user,
            get_object_business(obj),
        )

        return membership is not None and membership.role == Membership.Role.OWNER