from odoo import fields, models


class MgmtsystemHazardControlMeasureType(models.Model):
    _name = "mgmtsystem.hazard.control_measure.type"
    _description = "Type of Control Measure"

    company_id = fields.Many2one(
        "res.company", "Company", required=True, default=lambda self: self.env.company
    )
    name = fields.Char("Type", required=True, translate=True)
    description = fields.Text()
