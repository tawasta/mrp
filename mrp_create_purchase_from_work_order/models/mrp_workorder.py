from odoo import _, fields, models


class MrpWorkorder(models.Model):
    _inherit = "mrp.workorder"

    purchase_order_ids = fields.Many2many(
        comodel_name="purchase.order",
        relation="workorder_purchase_order_rel",
        column1="workorder_id",
        column2="purchase_order_id",
        string="Purchase Orders",
        help="Purchase Orders created from Work Order(s)",
        readonly=True,
        copy=False,
    )

    def workorder_to_purchase_wizard(self):
        view = self.env.ref(
            "mrp_create_purchase_from_work_order.view_workorder_purchase_form"
        )
        return {
            "name": _("Creating a purchase..."),
            "type": "ir.actions.act_window",
            "view_mode": "form",
            "res_model": "mrp.work.order.to.purchase",
            "views": [(view.id, "form")],
            "view_id": view.id,
            "target": "new",
            "context": dict(
                self.env.context, default_workorder_ids=[(4, w.id) for w in self]
            ),
        }
