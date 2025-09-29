from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    time_in_year = fields.Integer(
        string="Seconds in a year",
        related="company_id.time_in_year",
        readonly=False,
        help="Set the time parameter for LCA bom excel",
    )
    hide_by_product_sheet = fields.Boolean(
        string="Hide by-products Sheet",
        related="company_id.hide_by_product_sheet",
        readonly=False,
        help="Activate to hide by-products Sheet in LCA bom excel",
    )
    hide_operation_sheet = fields.Boolean(
        string="Hide operations, energy, consumption Sheet",
        related="company_id.hide_operation_sheet",
        readonly=False,
        help="Activate to hide operations Sheet in LCA bom excel",
    )
    hide_requirement_sheet = fields.Boolean(
        string="Hide product requirements Sheet",
        related="company_id.hide_requirement_sheet",
        readonly=False,
        help="Activate to hide requirements Sheet in LCA bom excel",
    )
    hide_summary_sheet = fields.Boolean(
        string="Hide Material summaries Sheet",
        related="company_id.hide_summary_sheet",
        readonly=False,
        help="Activate to hide summary Sheet in LCA bom excel",
    )
