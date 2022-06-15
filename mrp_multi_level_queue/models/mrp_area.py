from odoo import fields, models


class MrpArea(models.Model):
    _inherit = "mrp.area"

    current_llc_calculation = fields.Integer(
        string="Current LLC calculation",
        help="Technical field to help with asynchronous LLC calculation. "
             "Set to -1 to allow running MRP calculation again",
        default=-1
    )
