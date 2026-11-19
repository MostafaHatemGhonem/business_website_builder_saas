from django.db import IntegrityError, transaction
from django.test import TestCase

from apps.businesses.models import Business
from .models import Category


class CategorySlugConstraintTests(TestCase):
    def setUp(self):
        self.business_a = Business.objects.create(
            name="Burger Spot",
            slug="burger-spot",
            business_type="restaurant",
        )
        self.business_b = Business.objects.create(
            name="Grill House",
            slug="grill-house",
            business_type="restaurant",
        )

    def test_different_businesses_can_share_category_slug(self):
        cat_a = Category.objects.create(
            business=self.business_a,
            name="Burgers",
            slug="burgers",
        )
        cat_b = Category.objects.create(
            business=self.business_b,
            name="Burgers",
            slug="burgers",
        )
        self.assertEqual(cat_a.slug, "burgers")
        self.assertEqual(cat_b.slug, "burgers")

    def test_same_business_cannot_have_duplicate_category_slug(self):
        Category.objects.create(
            business=self.business_a,
            name="Burgers",
            slug="burgers",
        )
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Category.objects.create(
                    business=self.business_a,
                    name="Special Burgers",
                    slug="burgers",
                )
