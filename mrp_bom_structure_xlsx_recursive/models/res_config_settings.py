from odoo import fields, models


class ResConfigSettings(models.TransientModel):

    _inherit = "res.config.settings"

    time_in_year = fields.Integer(
        string="Seconds in a year",
        related="company_id.time_in_year",
        readonly=False,
        help="Set the time parameter for LCA bom excel",
    )
