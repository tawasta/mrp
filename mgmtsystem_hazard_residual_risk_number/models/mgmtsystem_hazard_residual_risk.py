from odoo import fields, models


class MgmtsystemHazardResidualRisk(models.Model):
    _inherit = "mgmtsystem.hazard.residual_risk"

    # Follows the residual risk computation of mgmtsystem_hazard_risk, which uses
    # the same formula as the risk of the hazard
    risk_number = fields.Integer(string="Risk number", related="risk")
