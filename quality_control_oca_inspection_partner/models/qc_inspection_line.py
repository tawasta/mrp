from odoo import fields, models


class QcInspectionLine(models.Model):
    _inherit = "qc.inspection.line"

    partner_id = fields.Many2one(
        comodel_name="res.partner",
        string="Partner",
        related="inspection_id.partner_id",
        store=True,
    )
