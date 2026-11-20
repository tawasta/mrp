from odoo import fields, models


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    workorder_ids = fields.Many2many(
        comodel_name="mrp.workorder",
        relation="workorder_purchase_order_rel",
        column1="purchase_order_id",
        column2="workorder_id",
        help="Work Orders the Purchase(s) originated from",
        readonly=True,
        copy=False,
    )
