from odoo import api, fields, models


class MrpRoutingWorkcenter(models.Model):

    _inherit = "mrp.routing.workcenter"

    bom_consu = fields.Many2one(related="workcenter_id.bom_consu")
    duration_passive = fields.Float(string="Passive Duration")
    duration_active = fields.Float(string="Active Duration")
    duration_total = fields.Float(
        string="Total Duration", compute=lambda self: self._compute_duration_total()
    )

    @api.depends("duration_passive", "duration_active")
    def _compute_duration_total(self):
        for center in self:
            center.duration_total = center.duration_passive + center.duration_active
