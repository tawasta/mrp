from odoo import _, models


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    def button_mark_done_with_message(self):
        view = self.env.ref("mrp_production_produce_confirm_message.view_message_form")
        return {
            "name": _("Produce all?"),
            "type": "ir.actions.act_window",
            "view_mode": "form",
            "res_model": "mrp.production.message.wizard",
            "views": [(view.id, "form")],
            "view_id": view.id,
            "target": "new",
            "context": dict(
                self.env.context, default_production_ids=[(p.id) for p in self]
            ),
        }
