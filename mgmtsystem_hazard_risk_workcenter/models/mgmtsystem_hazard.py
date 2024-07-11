from odoo import fields, models


class MgmtsystemHazard(models.Model):

    _inherit = "mgmtsystem.hazard"

    workcenter_id = fields.Many2one("mrp.workcenter", string="Workcenter")
