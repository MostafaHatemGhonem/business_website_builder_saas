from importlib import import_module
from types import SimpleNamespace
from unittest.mock import MagicMock

from django.test import SimpleTestCase

from .models import WebsiteSection


class WebsiteSectionChoiceTests(SimpleTestCase):
    def test_product_grid_choice_value_and_label(self):
        self.assertEqual(WebsiteSection.Type.PRODUCT_GRID, "Product_grid")
        self.assertEqual(WebsiteSection.Type.PRODUCT_GRID.label, "product_grid")
        self.assertNotIn("Product_gird", WebsiteSection.Type.values)
        self.assertEqual(
            WebsiteSection.Type.values,
            ["Hero", "Product_grid", "Gallery"],
        )

    def test_websitesection_display_uses_corrected_choice(self):
        section = WebsiteSection(type=WebsiteSection.Type.PRODUCT_GRID)
        self.assertEqual(section.get_type_display(), "product_grid")


class WebsiteSectionMigrationTests(SimpleTestCase):
    def test_migration_uses_connection_alias_for_forward_and_reverse(self):
        migration_mod = import_module(
            "apps.websites.migrations.0003_alter_websitesection_type"
        )
        schema_editor = SimpleNamespace(connection=SimpleNamespace(alias="replica"))

        model = MagicMock()
        apps = MagicMock()
        apps.get_model.return_value = model

        migration_mod.migrate_product_grid_forward(apps, schema_editor)
        apps.get_model.assert_called_with("websites", "WebsiteSection")
        model.objects.using.assert_called_with("replica")
        model.objects.using.return_value.filter.assert_called_with(type="Product_gird")
        model.objects.using.return_value.filter.return_value.update.assert_called_with(
            type="Product_grid"
        )

        model.reset_mock()
        migration_mod.migrate_product_grid_reverse(apps, schema_editor)
        model.objects.using.assert_called_with("replica")
        model.objects.using.return_value.filter.assert_called_with(type="Product_grid")
        model.objects.using.return_value.filter.return_value.update.assert_called_with(
            type="Product_gird"
        )
