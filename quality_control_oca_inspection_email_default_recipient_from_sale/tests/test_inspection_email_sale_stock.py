from odoo.addons.base.tests.common import BaseCommon


class TestInspectionEmailSaleStock(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.inspection_model = cls.env["qc.inspection"]
        cls.partner = cls.env["res.partner"].create({"name": "Sale Partner"})
        cls.sale = cls.env["sale.order"].create({"partner_id": cls.partner.id})
        cls.picking_type = cls.env.ref("stock.picking_type_out")
        cls.picking_with_sale = cls.env["stock.picking"].create(
            {
                "picking_type_id": cls.picking_type.id,
                "location_id": cls.picking_type.default_location_src_id.id,
                "location_dest_id": cls.picking_type.default_location_dest_id.id,
            }
        )
        cls.picking_with_sale.sale_id = cls.sale
        cls.picking_without_sale = cls.env["stock.picking"].create(
            {
                "picking_type_id": cls.picking_type.id,
                "location_id": cls.picking_type.default_location_src_id.id,
                "location_dest_id": cls.picking_type.default_location_dest_id.id,
            }
        )

    def test_default_recipients_include_sale_partner(self):
        inspection = self.inspection_model.create(
            {
                "name": "Test Inspection",
                "object_id": f"stock.picking,{self.picking_with_sale.id}",
            }
        )
        self.assertIn(self.partner, inspection.partner_inspection_email_recipient_ids)

    def test_no_recipients_when_no_sale(self):
        inspection = self.inspection_model.create(
            {
                "name": "Test Inspection 2",
                "object_id": f"stock.picking,{self.picking_without_sale.id}",
            }
        )
        self.assertFalse(inspection.partner_inspection_email_recipient_ids)
