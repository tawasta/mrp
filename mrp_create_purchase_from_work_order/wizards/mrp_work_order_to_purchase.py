from odoo import Command, api, fields, models


class MrpWorkOrderToPurchase(models.TransientModel):
    _name = "mrp.work.order.to.purchase"
    _description = "Work Order to Purchase order"

    workorder_ids = fields.Many2many(
        "mrp.workorder",
    )
    product_ids = fields.Many2many(
        "product.product", default=lambda self: self._get_default_products()
    )
    partner_id = fields.Many2one("res.partner")
    product_qty = fields.Float(string="Quantity", default=1)
    picking_type_id = fields.Many2one(
        comodel_name="stock.picking.type",
        string="Delivery Location",
        required=True,
        default=lambda self: self._get_default_picking_type(),
    )

    def _get_default_products(self):
        workorders = self.env["mrp.workorder"].browse(self._context.get("active_ids"))
        products = self.env["product.product"]
        for wo in workorders:
            if wo.purchase_product_id:
                products |= wo.purchase_product_id
        return products

    def _get_default_picking_type(self):
        type_obj = self.env["stock.picking.type"]
        company_id = self.env.context.get("company_id") or self.env.company.id
        types = type_obj.search(
            [("code", "=", "incoming"), ("warehouse_id.company_id", "=", company_id)]
        )
        if not types:
            types = type_obj.search(
                [("code", "=", "incoming"), ("warehouse_id", "=", False)]
            )
        return types[:1]

    @api.model
    def create_purchase(self):
        purchase_order_model = self.env["purchase.order"]

        manuf_id = self.workorder_ids and self.workorder_ids[0].production_id

        initial_values = {
            "partner_id": self.partner_id.id,
            "company_id": self.env.company.id,
            "currency_id": self.env.company.currency_id.id,
            "picking_type_id": self.picking_type_id.id,
            "origin": manuf_id.name,
            "workorder_ids": [Command.set(self.workorder_ids.ids)],
            "payment_term_id": self.partner_id.property_supplier_payment_term_id.id,
        }

        updated_values = purchase_order_model.play_onchanges(
            initial_values, ["partner_id"]
        )

        return purchase_order_model.create(updated_values)

    @api.model
    def create_purchase_line(self, product, partner_id, purchase_order):
        purchase_order_line_model = self.env["purchase.order.line"]

        initial_values = {
            "order_id": purchase_order.id,
            "product_id": product.id,
            "product_qty": self.product_qty,
            "product_uom": product.uom_id.id,
            "partner_id": partner_id.id,
        }

        order_line = purchase_order_line_model.create(initial_values)
        order_line._compute_price_unit_and_date_planned_and_name()

        return order_line

    def button_create_purchase(self):
        self.ensure_one()

        po_res = self.create_purchase()
        products = self.product_ids
        partner = self.partner_id

        for product in products:
            self.create_purchase_line(product, partner, po_res)

        return {
            "view_type": "form",
            "view_mode": "form",
            "res_model": "purchase.order",
            "type": "ir.actions.act_window",
            "res_id": po_res.id,
            "context": self.env.context,
        }
