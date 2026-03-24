from odoo import _, api, fields, models


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

    purchase_order_status = fields.Text(
        string="PO status", compute=lambda self: self._compute_purchase_order_status()
    )

    purchase_cost = fields.Float(compute=lambda self: self._compute_purchase_cost())

    def _compute_purchase_cost(self):
        for workorder in self:
            purchase_cost = 0

            for purchase in workorder.purchase_order_ids:
                po_lines = purchase.order_line.filtered(
                    lambda line, workorder=workorder: line.product_id
                    in workorder.move_raw_ids.mapped("product_id")
                )
                for po_line in po_lines:
                    purchase_cost += po_line.price_unit * po_line.product_qty
            workorder.purchase_cost = purchase_cost

    @api.depends("purchase_order_ids")
    def _compute_purchase_order_status(self):
        """Computes purchase statuses"""
        for wo in self:
            if wo.purchase_order_ids:
                po_status = []
                for po in wo.purchase_order_ids:
                    state = dict(po._fields["state"].selection).get(po.state)
                    po_status.append(state)
                wo.purchase_order_status = ", ".join(po_status)
            else:
                wo.purchase_order_status = ""

    def workorder_to_purchase_wizard(self):
        """This opens up a wizard to create purchases"""
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
