from odoo import fields, models


class QcInspection(models.Model):
    _inherit = "qc.inspection"

    inspection_email_sent = fields.Boolean(
        string="Inspection E-mail Sent",
        copy=False,
        help="Have the inspection results already been communicated to their "
        "recipients by e-mail.",
        tracking=True,
    )

    def action_send_by_email(self):
        self.ensure_one()
        template = self.env.ref(
            "quality_control_oca_inspection_email.mail_template_qc_inspection",
            raise_if_not_found=False,
        )
        ctx = {
            "default_model": "qc.inspection",
            "default_res_ids": self.ids,
            "default_composition_mode": "comment",
            "default_email_layout_xmlid": (
                "mail.mail_notification_layout_with_responsible_signature"
            ),
            "force_email": True,
            "mark_qc_inspection_email_as_sent": True,
        }
        if template:
            ctx["default_template_id"] = template.id
        return {
            "name": self.env._("Send Inspection Results by E-mail"),
            "type": "ir.actions.act_window",
            "view_mode": "form",
            "res_model": "mail.compose.message",
            "views": [(False, "form")],
            "target": "new",
            "context": ctx,
        }

    def message_post(self, **kwargs):
        if self.env.context.get("mark_qc_inspection_email_as_sent"):
            self.write({"inspection_email_sent": True})
        return super().message_post(**kwargs)
