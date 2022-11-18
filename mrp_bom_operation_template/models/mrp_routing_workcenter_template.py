from odoo import fields, models


class MrpRoutingWorkcenterTemplate(models.Model):

    _name = "mrp.routing.workcenter.template"
    _description = "Mrp Routing Workcenter Template"
    _order = "sequence, id"

    name = fields.Char("Operation", required=True)
    workcenter_id = fields.Many2one(
        "mrp.workcenter", "Work Center", required=True, check_company=True
    )
    sequence = fields.Integer(
        "Sequence",
        default=100,
        help="Gives the sequence order when displaying a list of routing Work Centers.",
    )
    time_mode = fields.Selection(
        [
            ("auto", "Compute based on tracked time"),
            ("manual", "Set duration manually"),
        ],
        string="Duration Computation",
        default="manual",
    )
    time_mode_batch = fields.Integer("Based on", default=10)
    time_cycle_manual = fields.Float(
        "Manual Duration",
        default=60,
        help="Time in minutes:"
        "- In manual mode, time used"
        "- In automatic mode, supposed first time when there aren't any work orders yet",
    )
    company_id = fields.Many2one(
        "res.company", "Company", default=lambda self: self.env.company
    )
    routing_ids = fields.One2many(
        "mrp.routing.workcenter", "template_id", string="Routing workcenter"
    )
