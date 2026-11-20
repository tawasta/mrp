from odoo import fields, models


class MrpWorkcenter(models.Model):
    _inherit = "mrp.workcenter"

    is_subcontractor = fields.Boolean(default=False)

    default_purchase_product_id = fields.Many2one(
        "product.product", string="Default Product to purchase"
    )
