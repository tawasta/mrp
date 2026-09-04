from odoo.tests import Form, tagged

from odoo.addons.base.tests.common import BaseCommon


@tagged("post_install", "-at_install")
class TestReportLang(BaseCommon):
    """The PDF must render in the report partner's language, not in the
    language of whoever happens to be printing it."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env["res.lang"]._activate_lang("fi_FI")
        cls.report_ref = (
            "quality_control_oca_inspection_report.action_report_qc_inspection"
        )
        cls.inspection_model = cls.env["qc.inspection"]
        cls.fi_partner = cls.env["res.partner"].create(
            {"name": "QC Lang Suomi", "lang": "fi_FI"}
        )
        cls.no_lang_partner = cls.env["res.partner"].create(
            {"name": "QC Lang None", "lang": False}
        )
        cls.product = cls.env["product.product"].create(
            {"name": "QC Lang Product", "type": "consu"}
        )
        cls.picking_type = cls.env.ref("stock.picking_type_out")

        # The company report title is translatable and is read off the record,
        # so it proves the rendering context language reached the records --
        # without depending on the module's .po terms being loaded in the
        # test database.
        cls.company = cls.env.company
        cls.company.qc_inspection_report_title = "Inspection Report"
        cls.company.with_context(
            lang="fi_FI"
        ).qc_inspection_report_title = "Tarkastusraportti"

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
                "name": "Lang Test Inspection",
                "object_id": f"{record._name},{record.id}",
            }
        )

    def _render(self, inspection):
        html, _ = self.env["ir.actions.report"]._render_qweb_html(
            self.report_ref, inspection.ids
        )
        return html

    def test_report_partner_taken_from_picking(self):
        inspection = self._inspection_for(self._new_picking(self.fi_partner))
        self.assertEqual(inspection._get_report_partner(), self.fi_partner)

    def test_report_lang_follows_partner(self):
        inspection = self._inspection_for(self._new_picking(self.fi_partner))
        self.assertEqual(inspection._get_report_lang(), "fi_FI")

    def test_report_lang_falls_back_to_user_lang(self):
        inspection = self._inspection_for(self._new_picking(self.no_lang_partner))
        self.assertEqual(inspection._get_report_lang(), self.env.lang)

    def test_report_lang_falls_back_without_partner(self):
        """A product reference yields no partner at all."""
        inspection = self._inspection_for(self.product)
        self.assertFalse(inspection._get_report_partner())
        self.assertEqual(inspection._get_report_lang(), self.env.lang)

    def test_rendered_report_uses_partner_lang(self):
        inspection = self._inspection_for(self._new_picking(self.fi_partner))
        html = self._render(inspection.with_context(lang="en_US"))
        self.assertIn(b"Tarkastusraportti", html)
        self.assertNotIn(b"Inspection Report", html)

    def test_rendered_report_uses_user_lang_without_partner_lang(self):
        inspection = self._inspection_for(self._new_picking(self.no_lang_partner))
        html = self._render(inspection.with_context(lang="en_US"))
        self.assertIn(b"Inspection Report", html)
        self.assertNotIn(b"Tarkastusraportti", html)

    def test_partner_name_shown_as_customer(self):
        inspection = self._inspection_for(self._new_picking(self.fi_partner))
        html = self._render(inspection)
        self.assertIn(self.fi_partner.name.encode(), html)

    def test_report_renders_for_product_reference(self):
        """product.product has no partner_id field at all; resolving the
        customer must not raise for such a reference."""
        inspection = self._inspection_for(self.product)
        html = self._render(inspection)
        self.assertIn(b"Lang Test Inspection", html)

    def test_report_renders_for_lot_reference(self):
        """Same for stock.lot, the other partnerless reference target."""
        if "stock.lot" not in dict(self.inspection_model.object_selection_values()):
            self.skipTest("stock.lot is not an inspection reference target")
        lot = self.env["stock.lot"].create(
            {"name": "QC Lang Lot", "product_id": self.product.id}
        )
        inspection = self._inspection_for(lot)
        html = self._render(inspection)
        self.assertIn(b"Lang Test Inspection", html)
