from odoo.tests import tagged

from odoo.addons.base.tests.common import BaseCommon


@tagged("post_install", "-at_install")
class TestInspectionSaleLink(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.inspection_model = cls.env["qc.inspection"]
        cls.partner = cls.env["res.partner"].create({"name": "Sale Link Partner"})
        cls.sale = cls.env["sale.order"].create({"partner_id": cls.partner.id})
        cls.other_sale = cls.env["sale.order"].create({"partner_id": cls.partner.id})
        cls.product = cls.env["product.product"].create(
            {"name": "Sale Link Product", "type": "consu"}
        )

    def _create_inspection(self, object_ref):
        return self.inspection_model.create(
            {
                "name": "Test Inspection",
                "object_id": f"{object_ref._name},{object_ref.id}",
            }
        )

    def test_object_selection_values_contains_sale_order(self):
        values = dict(self.inspection_model.object_selection_values())
        self.assertEqual(values.get("sale.order"), "Sale Order")

    def test_sale_order_id_computed_from_reference(self):
        inspection = self._create_inspection(self.sale)
        self.assertEqual(inspection.sale_order_id, self.sale)

    def test_sale_order_id_false_for_non_sale_reference(self):
        inspection = self._create_inspection(self.product)
        self.assertFalse(inspection.sale_order_id)

    def test_sale_order_id_recomputes_on_reference_change(self):
        inspection = self._create_inspection(self.sale)
        self.assertEqual(inspection.sale_order_id, self.sale)
        inspection.object_id = f"sale.order,{self.other_sale.id}"
        self.assertEqual(inspection.sale_order_id, self.other_sale)

    def test_inspection_line_sale_order_id_related(self):
        inspection = self._create_inspection(self.sale)
        line = self.env["qc.inspection.line"].create(
            {"inspection_id": inspection.id, "name": "Question"}
        )
        self.assertEqual(line.sale_order_id, self.sale)

    def test_sale_order_smart_button_fields(self):
        self.assertEqual(self.sale.qc_inspection_count, 0)
        self.assertFalse(self.sale.qc_inspection_ids)
        first = self._create_inspection(self.sale)
        second = self._create_inspection(self.sale)
        self._create_inspection(self.other_sale)
        self.sale.invalidate_recordset(["qc_inspection_ids", "qc_inspection_count"])
        self.assertEqual(self.sale.qc_inspection_count, 2)
        self.assertEqual(self.sale.qc_inspection_ids, first | second)
        self.assertEqual(self.other_sale.qc_inspection_count, 1)

    def test_default_get_prefills_object_id_from_context(self):
        res = self.inspection_model.with_context(
            active_model="sale.order", active_id=self.sale.id
        ).default_get(["object_id"])
        self.assertEqual(res.get("object_id"), f"sale.order,{self.sale.id}")

    def test_sale_order_id_from_picking_when_stock_glue_installed(self):
        """When quality_control_stock_oca + sale_stock are installed, an
        inspection referencing a delivery links to that delivery's sale order."""
        inspection_fields = self.inspection_model._fields
        if "picking_id" not in inspection_fields:
            self.skipTest("quality_control_stock_oca not installed")
        picking_type = self.env.ref("stock.picking_type_out")
        if "sale_id" not in self.env["stock.picking"]._fields:
            self.skipTest("sale_stock not installed")
        picking = self.env["stock.picking"].create(
            {
                "picking_type_id": picking_type.id,
                "location_id": picking_type.default_location_src_id.id,
                "location_dest_id": picking_type.default_location_dest_id.id,
            }
        )
        picking.sale_id = self.sale
        inspection = self._create_inspection(picking)
        self.assertEqual(inspection.sale_order_id, self.sale)

    def test_default_get_ignores_unrelated_context(self):
        res = self.inspection_model.with_context(
            active_model="product.product", active_id=self.product.id
        ).default_get(["object_id"])
        self.assertFalse(res.get("object_id"))
