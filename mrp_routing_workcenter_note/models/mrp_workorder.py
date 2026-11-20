from odoo import api, fields, models
from odoo.tools import is_html_empty


class MrpWorkorder(models.Model):
    _inherit = "mrp.workorder"

    operation_note = fields.Html(
        "Description", related="operation_id.note", readonly=True
    )
    # The editor keeps empty markup when the description is cleared
    has_operation_note = fields.Boolean(compute="_compute_has_operation_note")

    @api.depends("operation_note")
    def _compute_has_operation_note(self):
        for workorder in self:
            workorder.has_operation_note = not is_html_empty(workorder.operation_note)
