from odoo import fields, models


class ProductProduct(models.Model):

    _inherit = "product.product"

    multiply_with_partial_weight = fields.Boolean(
        string="Multiply with Partial weight",
        store=True,
        help="Used in LCA BoM computations",
        copy=False,
    )

    multiply_with_by_products = fields.Boolean(
        string="Multiply with By-products",
        store=True,
        help="Used in LCA BoM computations",
        copy=False,
    )

    ignore_component_qty = fields.Boolean(
        string="Ignore component quantity",
        store=True,
        help="Used in LCA BoM computations",
        copy=False,
    )
