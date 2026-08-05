from odoo import api, fields, models


class QcInspectionLine(models.Model):
    _inherit = "qc.inspection.line"

    question_type = fields.Selection(
        selection_add=[("freetext", "Freetext")],
    )
    freetext_value = fields.Text(
        help="Manually entered answer for freetext questions.",
    )

    @api.depends("freetext_value")
    def _compute_quality_test_check(self):
        """Freetext answers always succeed,  they are informational only."""
        res = super()._compute_quality_test_check()
        for inspection_line in self.filtered(
            lambda line: line.question_type == "freetext"
        ):
            inspection_line.success = True
        return res
