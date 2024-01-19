from odoo import fields, models


class MrpBomComponentChangeWizard(models.TransientModel):

    _name = "mrp.bom.component.change.wizard"

    product_id = fields.Many2one("product.product", string="Product")
    bom_line_ids = fields.Many2many(
        "mrp.bom.line",
        string="Components",
        default=lambda self: self.default_bom_lines(),
    )

    def default_bom_lines(self):
        return self.env["mrp.bom.line"].browse(self._context.get("active_ids"))

    def confirm_message_wizard(self):

        components = self.bom_line_ids
        msg_confirm_wiz = self.env[
            "mrp.component.change.message.confirm.wizard"
        ].create(
            {"bom_line_ids": [(6, 0, components.ids)], "product_id": self.product_id.id}
        )

        return {
            "type": "ir.actions.act_window",
            "res_model": "mrp.component.change.message.confirm.wizard",
            "view_type": "form",
            "view_mode": "form",
            "res_id": msg_confirm_wiz.id,
            "target": "new",
        }
