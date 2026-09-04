from odoo import models


class QcInspection(models.Model):
    _inherit = "qc.inspection"

    def _get_report_partner(self):
        """Partner the report is addressed to.

        Drives both the printed Customer row and the report language. Reads the
        partner straight off the referenced document, when that document has
        a partner_id field."""
        self.ensure_one()
        obj = self.object_id
        # object_id may reference a product or a lot, which have no partner
        if obj and "partner_id" in obj._fields and obj.partner_id:
            return obj.partner_id[:1]
        return self.env["res.partner"]

    def _get_report_lang(self):
        """Language for the PDF: the partner's, falling back to the user's."""
        self.ensure_one()
        return self._get_report_partner().lang or self.env.lang

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
