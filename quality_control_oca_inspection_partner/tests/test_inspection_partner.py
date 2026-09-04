from odoo.tests import tagged

from odoo.addons.base.tests.common import BaseCommon


@tagged("post_install", "-at_install")
class TestInspectionPartner(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.inspection_model = cls.env["qc.inspection"]
        cls.partner_a = cls.env["res.partner"].create({"name": "QC Partner A"})
        cls.partner_b = cls.env["res.partner"].create({"name": "QC Partner B"})
        cls.partner_manual = cls.env["res.partner"].create(
            {"name": "QC Partner Manual"}
        )
        cls.product = cls.env["product.product"].create(
            {"name": "QC Partner Product", "type": "consu"}
        )
        cls.selection = dict(cls.inspection_model.object_selection_values())
        cls.sale_supported = "sale.order" in cls.selection
        if cls.sale_supported:
            cls.sale_a = cls.env["sale.order"].create({"partner_id": cls.partner_a.id})
            cls.sale_b = cls.env["sale.order"].create({"partner_id": cls.partner_b.id})

    def _create_inspection(self, object_ref, **vals):
        return self.inspection_model.create(
            {
                "name": "Test Inspection",
                "object_id": f"{object_ref._name},{object_ref.id}",
                **vals,
            }
        )

    def _require_sale(self):
        if not self.sale_supported:
            self.skipTest(
                "sale.order is not an inspection reference target "
                "(quality_control_oca_inspection_sale_link not installed)"
            )

    def test_object_partner_field_names_default(self):
        self.assertEqual(
            self.inspection_model._object_partner_field_names(),
            ["partner_id", "commercial_partner_id"],
        )

    def test_partner_id_prefilled_from_reference(self):
        self._require_sale()
        inspection = self._create_inspection(self.sale_a)
        self.assertEqual(inspection.partner_id, self.partner_a)

    def test_partner_id_not_set_for_partnerless_reference(self):
        inspection = self._create_inspection(self.product)
        self.assertFalse(inspection.partner_id)

    def test_manual_partner_id_persists(self):
        self._require_sale()
        inspection = self._create_inspection(
            self.sale_a, partner_id=self.partner_manual.id
        )
        self.assertEqual(inspection.partner_id, self.partner_manual)
        # A write that does not touch object_id must not re-seed the partner.
        inspection.internal_notes = "touched"
        self.assertEqual(inspection.partner_id, self.partner_manual)

    def test_partner_id_reseeds_on_reference_change(self):
        self._require_sale()
        inspection = self._create_inspection(self.sale_a)
        self.assertEqual(inspection.partner_id, self.partner_a)
        inspection.object_id = f"sale.order,{self.sale_b.id}"
        self.assertEqual(inspection.partner_id, self.partner_b)

    def test_partner_id_kept_when_new_reference_has_no_partner(self):
        self._require_sale()
        inspection = self._create_inspection(self.sale_a)
        self.assertEqual(inspection.partner_id, self.partner_a)
        inspection.object_id = f"product.product,{self.product.id}"
        self.assertEqual(inspection.partner_id, self.partner_a)

    def test_direct_partner_reference(self):
        if "res.partner" not in self.selection:
            self.skipTest("res.partner is not an inspection reference target")
        inspection = self._create_inspection(self.partner_a)
        self.assertEqual(inspection.partner_id, self.partner_a)

    def test_inspection_line_partner_id_related(self):
        self._require_sale()
        inspection = self._create_inspection(self.sale_a)
        line = self.env["qc.inspection.line"].create(
            {"inspection_id": inspection.id, "name": "Question"}
        )
        self.assertEqual(line.partner_id, self.partner_a)

    def test_partner_id_change_tracked_in_chatter(self):
        self._require_sale()
        inspection = self._create_inspection(self.sale_a).with_context(
            tracking_disable=False,
            mail_create_nolog=False,
            mail_create_nosubscribe=False,
            mail_notrack=False,
        )
        inspection.partner_id = self.partner_manual
        inspection.flush_recordset()
        tracked = inspection.message_ids.tracking_value_ids.mapped("field_id.name")
        self.assertIn("partner_id", tracked)

    def test_partner_shown_in_report(self):
        self._require_sale()
        inspection = self._create_inspection(self.sale_a)
        self.assertEqual(inspection.partner_id, self.partner_a)
        html, _ = self.env["ir.actions.report"]._render_qweb_html(
            "quality_control_oca_inspection_report.action_report_qc_inspection",
            inspection.ids,
        )
        self.assertIn(self.partner_a.name.encode(), html)

    def test_report_partner_is_the_inspection_partner(self):
        """The inspection's own partner_id decides who the report is for,
        rather than the referenced document."""
        self._require_sale()
        inspection = self._create_inspection(
            self.sale_a, partner_id=self.partner_manual.id
        )
        self.assertEqual(inspection._get_report_partner(), self.partner_manual)

    def test_manual_partner_decides_report_lang(self):
        """A manually set partner overrides the referenced document for the
        report language too, not just for the printed customer."""
        self._require_sale()
        self.env["res.lang"]._activate_lang("fi_FI")
        self.partner_manual.lang = "fi_FI"
        inspection = self._create_inspection(
            self.sale_a, partner_id=self.partner_manual.id
        )
        self.assertEqual(inspection._get_report_lang(), "fi_FI")

    def test_report_lang_falls_back_without_partner(self):
        inspection = self._create_inspection(self.product)
        self.assertFalse(inspection.partner_id)
        self.assertEqual(inspection._get_report_lang(), self.env.lang)
