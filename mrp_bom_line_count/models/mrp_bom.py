from odoo import fields, models, api


class MrpBom(models.Model):
    _inherit = "mrp.bom"

    bom_line_count = fields.Integer(
        "BoM line count",
        store=True,
        compute="_compute_bom_line_count",
    )

    @api.depends("bom_line_ids")
    def _compute_bom_line_count(self):
        for record in self:
            record.bom_line_count = len(record.bom_line_ids)
