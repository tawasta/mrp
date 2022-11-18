from odoo import api, fields, models


class MrpRoutingWorkcenter(models.Model):

    _inherit = "mrp.routing.workcenter"

    template_id = fields.Many2one(
        "mrp.routing.workcenter.template", string="Used template"
    )

    @api.onchange("template_id")
    def onchange_template_id(self):
        template = self.template_id

        if template:
            self.name = template.name
            self.workcenter_id = template.workcenter_id.id
            self.sequence = template.sequence
            self.time_mode = template.time_mode
            self.time_cycle_manual = template.time_cycle_manual
            self.company_id = template.company_id.id
