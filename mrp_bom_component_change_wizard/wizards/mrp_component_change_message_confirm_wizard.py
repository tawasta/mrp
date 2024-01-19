from odoo import fields, models


class MrpComponentChangeMessageConfirmWizard(models.TransientModel):

    _name = "mrp.component.change.message.confirm.wizard"

    product_id = fields.Many2one("product.product", string="Product")
    bom_line_ids = fields.Many2many("mrp.bom.line", string="Components")

    def change(self):
        components = self.bom_line_ids

        for component in components:
            component.product_id = self.product_id
