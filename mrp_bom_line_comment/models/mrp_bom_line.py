from odoo import fields, models


class MrpBom(models.Model):
    _inherit = "mrp.bom.line"

    comment = fields.Char(
        help="A free comment. Has no functional purpose on manufacturing",
    )
