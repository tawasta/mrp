
from odoo import fields, models


class MrpBomLine(models.Model):

    _inherit = "mrp.bom.line"

    product_reference = fields.Char(related="product_id.default_code")
