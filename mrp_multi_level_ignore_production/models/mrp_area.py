
from odoo import fields, models


class MrpArea(models.Model):

    _inherit = 'mrp.area'

    ignore_production_orders = fields.Boolean(
        string="Ignore manufacturing orders",
        help="Select to ignore manufacturing orders"
    )
