from odoo import api, fields, models


class QcInspection(models.Model):
    _inherit = "qc.inspection"

    sale_order_id = fields.Many2one(
        comodel_name="sale.order",
        string="Sale Order",
        compute="_compute_sale_order_id",
        store=True,
    )

    def object_selection_values(self):
        result = super().object_selection_values()
        result.append(("sale.order", "Sale Order"))
        return result

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        ctx = self.env.context
        if (
            "object_id" in fields_list
            and not res.get("object_id")
            and ctx.get("active_model") == "sale.order"
            and ctx.get("active_id")
        ):
            res["object_id"] = f"sale.order,{ctx['active_id']}"
        return res

    @api.depends("object_id")
    def _compute_sale_order_id(self):
        # ``picking_id`` is only present when ``quality_control_stock_oca`` is
        # installed, and ``stock.picking.sale_id`` only when ``sale_stock`` is.
        has_picking = "picking_id" in self._fields
        for inspection in self:
            obj = inspection.object_id
            order = self.env["sale.order"]
            if obj and obj._name == "sale.order":
                order = obj
            elif (
                has_picking
                and obj
                and obj._name == "stock.picking"
                and "sale_id" in inspection.picking_id._fields
            ):
                order = inspection.picking_id.sale_id
            inspection.sale_order_id = order
