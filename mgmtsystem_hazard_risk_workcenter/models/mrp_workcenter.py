from odoo import fields, models


class MrpWorkcenter(models.Model):

    _inherit = "mrp.workcenter"

    hazard_ids = fields.One2many("mgmtsystem.hazard", "workcenter_id", string="Hazards")
