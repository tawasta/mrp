from odoo import fields, models


class MrpProduction(models.Model):

    _inherit = "mrp.production"

    unbuild_note = fields.Selection(
        [("unbuilt", "UNBUILT")],
        readonly=True,
        default=False,
        copy=False,
        string="Unbuilt",
    )
