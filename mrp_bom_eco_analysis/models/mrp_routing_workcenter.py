from odoo import api, fields, models


class MrpRoutingWorkcenter(models.Model):

    _inherit = "mrp.routing.workcenter"

    person_count = fields.Integer(string="Number of persons")
    bom_consu = fields.Many2one(related="workcenter_id.bom_consu")
    duration_person = fields.Float(string="Personnel working time")
    duration_passive = fields.Float(string="Passive Duration")
    duration_active = fields.Float(string="Active Duration")
    duration_total = fields.Float(
        string="Total Duration", compute=lambda self: self._compute_duration_total()
    )

    @api.onchange("duration_passive", "duration_active", "time_cycle_manual")
    def onchange_duration_person(self):
        for center in self:
            center.duration_person = (
                center.time_cycle_manual
                + center.duration_passive
                + center.duration_active
            )

    @api.depends("duration_passive", "duration_active")
    def _compute_duration_total(self):
        for center in self:
            center.duration_total = center.duration_passive + center.duration_active
