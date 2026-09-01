from odoo import fields, models


class QcInspectionLine(models.Model):
    _inherit = "qc.inspection.line"

    # Connect also QC lines to SOs for potential reporting purposes
    sale_order_id = fields.Many2one(
        comodel_name="sale.order",
        string="Sale Order",
        related="inspection_id.sale_order_id",
        store=True,
    )
