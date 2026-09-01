from odoo.addons.base.tests.common import BaseCommon


class TestReportTrimDecimals(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.inspection = cls.env["qc.inspection"].create({"name": "Trim Test"})
        cls.line = cls.env["qc.inspection.line"].create(
            {
                "inspection_id": cls.inspection.id,
                "name": "Measure",
                "question_type": "quantitative",
                "quantitative_value": 12.3,
            }
        )
        cls.report_ref = (
            "quality_control_oca_inspection_report.action_report_qc_inspection"
        )

    def _render(self):
        html, _ = self.env["ir.actions.report"]._render_qweb_html(
            self.report_ref, self.inspection.ids
        )
        return html

    def test_no_trim_keeps_full_precision(self):
        self.assertEqual(
            self.line._report_format_quantitative_value(trim=False), "12.30000"
        )

    def test_trim_drops_trailing_zeros(self):
        self.assertEqual(self.line._report_format_quantitative_value(trim=True), "12.3")

    def test_trim_whole_number_has_no_decimals(self):
        self.line.quantitative_value = 12.0
        self.assertEqual(self.line._report_format_quantitative_value(trim=True), "12")

    def test_report_full_precision_by_default(self):
        self.assertFalse(self.env.company.qc_inspection_report_trim_decimals)
        self.assertIn(b"12.30000", self._render())

    def test_report_trimmed_when_enabled(self):
        self.env.company.qc_inspection_report_trim_decimals = True
        html = self._render()
        self.assertIn(b"12.3", html)
        self.assertNotIn(b"12.30000", html)
