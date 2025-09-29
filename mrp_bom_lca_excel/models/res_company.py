from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    time_in_year = fields.Integer(string="Seconds in a year")
    hide_by_product_sheet = fields.Boolean(
        string="Hide by-products Sheet",
    )
    hide_operation_sheet = fields.Boolean(
        string="Hide operations, energy, consumption Sheet",
    )
    hide_requirement_sheet = fields.Boolean(
        string="Hide product requirements Sheet",
    )
    hide_summary_sheet = fields.Boolean(
        string="Hide Material summaries Sheet",
    )
