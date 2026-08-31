from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    qc_inspection_ids = fields.One2many(
        comodel_name="qc.inspection",
        inverse_name="sale_order_id",
        string="Quality Inspections",
    )
    qc_inspection_count = fields.Integer(
        string="Inspections",
        compute="_compute_qc_inspection_count",
    )

    @api.depends("qc_inspection_ids")
    def _compute_qc_inspection_count(self):
        data = self.env["qc.inspection"]._read_group(
            domain=[("sale_order_id", "in", self.ids)],
            groupby=["sale_order_id"],
            aggregates=["__count"],
        )
        counts = {order.id: count for order, count in data}
        for order in self:
            order.qc_inspection_count = counts.get(order.id, 0)
