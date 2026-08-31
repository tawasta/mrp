from odoo import models
from odoo.tools import float_round, formatLang


class QcInspection(models.Model):
    _inherit = "qc.inspection"

    # report_notes = fields.Text(
    #     string="Notes",
    #     help="Free text shown in the Additional Information section of the "
    #     "inspection report.",
    # )

    # report_passed = fields.Boolean(
    #     string="Passed",
    #     compute="_compute_report_passed",
    # )

    # @api.depends("inspection_lines.success")
    # def _compute_report_passed(self):
    #     for inspection in self:
    #         lines = inspection.inspection_lines
    #         inspection.report_passed = bool(lines) and all(lines.mapped("success"))

    def _report_image_attachments(self):
        """Return image attachments posted in the chatter of this inspection."""
        self.ensure_one()
        messages = self.env["mail.message"].search(
            [("model", "=", self._name), ("res_id", "=", self.id)]
        )
        attachments = messages.attachment_ids | self.env["ir.attachment"].search(
            [
                ("res_model", "=", self._name),
                ("res_id", "=", self.id),
            ]
        )
        return attachments.filtered(
            lambda a: (a.mimetype or "").startswith("image/")
        ).sorted("id")


class QcInspectionLine(models.Model):
    _inherit = "qc.inspection.line"

    def _report_format_quantitative_value(self, trim=False):
        """Locale-formatted quantitative value for the PDF report.

        With ``trim`` (the company's ``qc_inspection_report_trim_decimals``
        setting), insignificant trailing zeros are dropped, e.g. ``12.30000``
        renders as ``12.3`` and ``12.00000`` as ``12``. Without it, the value
        keeps the full "Quality Control" decimal precision, matching the
        default ``t-field`` rendering.
        """
        self.ensure_one()
        max_digits = self.env["decimal.precision"].precision_get("Quality Control")
        digits = max_digits
        if trim:
            rounded = float_round(self.quantitative_value, precision_digits=max_digits)
            text = f"{rounded:.{max_digits}f}".rstrip("0").rstrip(".")
            digits = len(text.split(".", 1)[1]) if "." in text else 0
        return formatLang(self.env, self.quantitative_value, digits=digits)
