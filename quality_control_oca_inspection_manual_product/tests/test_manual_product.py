from odoo.exceptions import ValidationError
from odoo.tests import tagged

from odoo.addons.base.tests.common import BaseCommon


@tagged("post_install", "-at_install")
class TestManualProduct(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.inspection_model = cls.env["qc.inspection"]
        cls.product_a = cls.env["product.product"].create(
            {"name": "QC Manual Product A", "type": "consu"}
        )
        cls.product_b = cls.env["product.product"].create(
            {"name": "QC Manual Product B", "type": "consu"}
        )
        cls.selection = dict(cls.inspection_model.object_selection_values())
        cls.sale_supported = "sale.order" in cls.selection
        if cls.sale_supported:
            cls.partner = cls.env["res.partner"].create({"name": "QC Manual Partner"})
            cls.sale_a = cls.env["sale.order"].create({"partner_id": cls.partner.id})
            cls.sale_b = cls.env["sale.order"].create({"partner_id": cls.partner.id})

    def _create_inspection(self, object_ref):
        return self.inspection_model.create(
            {
                "name": "Test Inspection",
                "object_id": f"{object_ref._name},{object_ref.id}",
            }
        )

    def _require_sale(self):
        if not self.sale_supported:
            self.skipTest(
                "sale.order is not an inspection reference target "
                "(quality_control_oca_inspection_sale_link not installed)"
            )

    def test_product_id_is_editable(self):
        self.assertFalse(self.inspection_model._fields["product_id"].readonly)

    def test_manual_product_on_sale_order_reference(self):
        self._require_sale()
        inspection = self._create_inspection(self.sale_a)
        self.assertFalse(inspection.product_id)
        inspection.product_id = self.product_a
        self.assertEqual(inspection.product_id, self.product_a)

    def test_manual_product_survives_object_id_change(self):
        self._require_sale()
        inspection = self._create_inspection(self.sale_a)
        inspection.product_id = self.product_a
        inspection.object_id = f"sale.order,{self.sale_b.id}"
        self.assertEqual(inspection.product_id, self.product_a)

    def test_reference_product_overrides_prior_manual_value(self):
        self._require_sale()
        inspection = self._create_inspection(self.sale_a)
        inspection.product_id = self.product_b  # allowed: sale-order reference
        inspection.object_id = f"product.product,{self.product_a.id}"
        self.assertEqual(inspection.product_id, self.product_a)

    def test_manual_change_rejected_when_reference_has_product(self):
        inspection = self._create_inspection(self.product_a)
        self.assertEqual(inspection.product_id, self.product_a)
        with self.assertRaises(ValidationError):
            inspection.product_id = self.product_b
            inspection.env.flush_all()

    def test_setting_product_to_reference_value_is_allowed(self):
        inspection = self._create_inspection(self.product_a)
        inspection.product_id = self.product_a
        inspection.env.flush_all()
        self.assertEqual(inspection.product_id, self.product_a)

    def test_product_can_be_left_empty(self):
        self._require_sale()
        inspection = self._create_inspection(self.sale_a)
        inspection.internal_notes = "touched"
        self.assertFalse(inspection.product_id)

    def test_product_id_is_tracked(self):
        self.assertTrue(self.inspection_model._fields["product_id"].tracking)
