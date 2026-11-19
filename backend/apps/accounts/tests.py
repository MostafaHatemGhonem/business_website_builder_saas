from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.test import SimpleTestCase, TestCase
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from rest_framework import serializers

from .serializers import (
    PasswordResetConfirmSerializer,
    RegisterSerializer,
    UserSerializer,
)
from .views import PasswordResetConfirmView, PasswordResetView

User = get_user_model()


class AccountsConfigAndSerializerTests(SimpleTestCase):
    def test_user_serializer_excludes_password(self):
        fields = UserSerializer().get_fields()
        self.assertNotIn("password", fields)
        self.assertEqual(
            list(fields.keys()),
            ["id", "email", "first_name", "last_name"],
        )

    def test_register_serializer_rejects_weak_password(self):
        serializer = RegisterSerializer()
        with self.assertRaises(serializers.ValidationError) as ctx:
            serializer.validate(
                {
                    "email": "owner@example.com",
                    "first_name": "Test",
                    "last_name": "Owner",
                    "password": "123",
                }
            )
        self.assertIn("password", ctx.exception.detail)

    def test_register_serializer_rejects_password_similar_to_email_or_name(self):
        serializer = RegisterSerializer()
        with self.assertRaises(serializers.ValidationError) as ctx:
            serializer.validate(
                {
                    "email": "mostafa.cairo@example.com",
                    "first_name": "Mostafa",
                    "last_name": "Cairo",
                    "password": "mostafa1",
                }
            )
        self.assertIn("password", ctx.exception.detail)

        valid_attrs = {
            "email": "mostafa.cairo@example.com",
            "first_name": "Mostafa",
            "last_name": "Cairo",
            "password": "StrongUnrelated!Password99",
        }
        self.assertEqual(serializer.validate(valid_attrs), valid_attrs)

    def test_rest_framework_defaults_configured(self):
        drf = settings.REST_FRAMEWORK
        self.assertEqual(
            drf["DEFAULT_PERMISSION_CLASSES"],
            ["rest_framework.permissions.IsAuthenticated"],
        )
        self.assertEqual(
            drf["DEFAULT_AUTHENTICATION_CLASSES"],
            ["rest_framework.authentication.SessionAuthentication"],
        )
        self.assertEqual(
            drf["DEFAULT_PAGINATION_CLASS"],
            "rest_framework.pagination.PageNumberPagination",
        )
        self.assertEqual(drf["PAGE_SIZE"], 20)

    def test_password_reset_views_allow_any(self):
        from rest_framework.permissions import AllowAny

        self.assertEqual(PasswordResetView.permission_classes, [AllowAny])
        self.assertEqual(PasswordResetConfirmView.permission_classes, [AllowAny])


class AccountsDatabaseTests(TestCase):
    def test_register_serializer_hashes_password(self):
        serializer = RegisterSerializer(
            data={
                "email": "owner@example.com",
                "first_name": "Test",
                "last_name": "Owner",
                "password": "StrongPassword!234",
            }
        )
        self.assertTrue(serializer.is_valid(), serializer.errors)
        user = serializer.save()
        self.assertNotEqual(user.password, "StrongPassword!234")
        self.assertTrue(user.check_password("StrongPassword!234"))

    def test_inactive_user_cannot_confirm_password_reset(self):
        user = User.objects.create_user(
            email="inactive@example.com",
            password="OldStrongPassword!234",
            is_active=False,
        )
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)

        serializer = PasswordResetConfirmSerializer(
            data={
                "uid": uid,
                "token": token,
                "new_password": "NewStrongPassword!234",
            }
        )
        self.assertFalse(serializer.is_valid())
        self.assertIn("uid", serializer.errors)
