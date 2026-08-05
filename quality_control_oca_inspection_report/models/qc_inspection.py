from odoo import models


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
