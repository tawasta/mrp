from odoo import fields, models


class MrpRoutingWorkcenter(models.Model):
    # Operation model
    _inherit = "mrp.routing.workcenter"

    purchase_product_id = fields.Many2one(
        "product.product", string="Product to purchase"
    )
