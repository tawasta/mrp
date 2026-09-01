from odoo.tests import Form, tagged

from odoo.addons.base.tests.common import BaseCommon


@tagged("post_install", "-at_install")
class TestPartnerFromPickingSale(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.inspection_model = cls.env["qc.inspection"]
        cls.customer = cls.env["res.partner"].create({"name": "PPS Customer"})
        cls.customer2 = cls.env["res.partner"].create({"name": "PPS Customer 2"})
        cls.delivery_partner = cls.env["res.partner"].create({"name": "PPS Delivery"})
        cls.other_partner = cls.env["res.partner"].create({"name": "PPS Other"})
        cls.product = cls.env["product.product"].create(
            {"name": "PPS Product", "type": "consu"}
        )
        cls.picking_type = cls.env.ref("stock.picking_type_out")
        cls.sale = cls.env["sale.order"].create({"partner_id": cls.customer.id})

    @classmethod
    def _new_picking(cls, partner):
        picking_form = Form(
            cls.env["stock.picking"].with_context(
                default_picking_type_id=cls.picking_type.id
            )
        )
        picking_form.partner_id = partner
        with picking_form.move_ids.new() as move_form:
            move_form.product_id = cls.product
            move_form.product_uom_qty = 1
        return picking_form.save()

    def _inspection_for(self, record):
        return self.inspection_model.create(
            {
                "name": "Test Inspection",
                "object_id": f"{record._name},{record.id}",
            }
        )

    def test_partner_from_move_reference(self):
        picking = self._new_picking(self.delivery_partner)
        picking.sale_id = self.sale
        inspection = self._inspection_for(picking.move_ids)
        self.assertEqual(inspection.partner_id, self.customer)

    def test_partner_from_picking_reference(self):
        picking = self._new_picking(self.delivery_partner)
        picking.sale_id = self.sale
        inspection = self._inspection_for(picking)
        self.assertEqual(inspection.partner_id, self.customer)

    def test_fallback_to_picking_partner(self):
        picking = self._new_picking(self.delivery_partner)
        self.assertFalse(picking.sale_id)
        inspection = self._inspection_for(picking)
        self.assertEqual(inspection.partner_id, self.delivery_partner)

    def test_sale_partner_wins_over_move_partner(self):
        picking = self._new_picking(self.delivery_partner)
        picking.sale_id = self.sale
        picking.move_ids.partner_id = self.other_partner
        inspection = self._inspection_for(picking.move_ids)
        self.assertEqual(inspection.partner_id, self.customer)

    def test_non_picking_reference_unaffected(self):
        inspection = self._inspection_for(self.product)
        self.assertFalse(inspection.partner_id)

    def test_recompute_on_sale_partner_change(self):
        picking = self._new_picking(self.delivery_partner)
        picking.sale_id = self.sale
        inspection = self._inspection_for(picking)
        self.assertEqual(inspection.partner_id, self.customer)
        self.sale.partner_id = self.customer2
        self.assertEqual(inspection.partner_id, self.customer2)
