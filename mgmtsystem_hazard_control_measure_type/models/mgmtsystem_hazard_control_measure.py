from odoo import fields, models


class MgmtsystemHazardControlMeasure(models.Model):
    _inherit = "mgmtsystem.hazard.control_measure"

    type_id = fields.Many2one(
        "mgmtsystem.hazard.control_measure.type", string="Type", ondelete="restrict"
    )
