from odoo.addons.base.tests.common import BaseCommon


class TestInspectionFreetextSerial(BaseCommon):
    def test_search_by_serial_number(self):
        inspection_model = self.env["qc.inspection"]
        matching = inspection_model.create(
            {"name": "Inspection A", "serial_number": "SN-001"}
        )
        inspection_model.create({"name": "Inspection B", "serial_number": "SN-002"})
        found = inspection_model.search([("serial_number", "=", "SN-001")])
        self.assertEqual(found, matching)

    def test_serial_number_shown_in_report(self):
        inspection = self.env["qc.inspection"].create(
            {"name": "Inspection C", "serial_number": "SN-REPORT-XYZ"}
        )
        html, _ = self.env["ir.actions.report"]._render_qweb_html(
            "quality_control_oca_inspection_report.action_report_qc_inspection",
            inspection.ids,
        )
        self.assertIn(b"Serial Number / Identifier", html)
        self.assertIn(b"SN-REPORT-XYZ", html)
