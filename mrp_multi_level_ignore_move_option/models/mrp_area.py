
from odoo import fields, models


class MrpArea(models.Model):

    _inherit = 'mrp.area'

    ignore_production_orders = fields.Boolean(
        string="Ignore manufacturing orders",
        help="Select to ignore manufacturing orders"
    )

    ignore_purchase_orders = fields.Boolean(
        string="Ignore purchase orders",
        help="Select to ignore purchase orders. Use with CAUTION!"
    )
    ignore_sale_orders = fields.Boolean(
        string="Ignore sale orders",
        help="Select to ignore sale orders. Use with CAUTION!"
    )
