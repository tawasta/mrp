from odoo import fields, models


class ResConfigSettings(models.TransientModel):

    _inherit = "res.config.settings"

    minutes_in_year = fields.Integer(
        string="Minutes in a year",
        related="company_id.minutes_in_year",
        readonly=False,
        help="Set a minute parameter for LCA bom excel",
    )
