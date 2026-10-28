from odoo import api, fields, models


class MgmtsystemHazard(models.Model):
    _inherit = "mgmtsystem.hazard"

    # A list view cannot show the values of a One2many, so they are joined to a text.
    # Not stored: the risk number depends on the risk formula of the company.
    residual_risk_numbers = fields.Char(
        string="Residual risk numbers", compute="_compute_residual_risk_numbers"
    )

    @api.depends("residual_risk_ids.risk_number")
    def _compute_residual_risk_numbers(self):
        for hazard in self:
            numbers = hazard.residual_risk_ids.mapped("risk_number")
            hazard.residual_risk_numbers = ", ".join(
                str(number) for number in numbers if number
            )
