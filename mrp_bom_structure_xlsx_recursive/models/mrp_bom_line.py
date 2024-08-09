from odoo import fields, models


class MrpBomLine(models.Model):

    _inherit = "mrp.bom.line"

    alt_qty = fields.Float(
        string="Alternative Multiplier",
        copy=False,
        store=True,
        help="Used only in LCA BoM calculations.",
    )
