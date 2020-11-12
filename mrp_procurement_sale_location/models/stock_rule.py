from odoo import models


class StockRule(models.Model):
    _inherit = "stock.rule"

    def _get_stock_move_values(
        self,
        product_id,
        product_qty,
        product_uom,
        location_id,
        name,
        origin,
        values,
        group_id,
    ):
        # Override the procurement rule location with
        # sale order analytic account location

        res = super(StockRule, self)._get_stock_move_values(
            product_id,
            product_qty,
            product_uom,
            location_id,
            name,
            origin,
            values,
            group_id,
        )

        if values.get("sale_line_id"):
            sale_order = (
                self.env["sale.order.line"].browse([values["sale_line_id"]]).order_id
            )

            location = self._get_procurement_location(sale_order)

            if location:
                res["location_id"] = location.id
        return res

    def _prepare_mo_vals(
        self,
        product_id,
        product_qty,
        product_uom,
        location_id,
        name,
        origin,
        values,
        bom,
    ):
        # Override the MO source and destination location with
        # sale order analytic account location

        res = super(StockRule, self)._prepare_mo_vals(
            product_id, product_qty, product_uom, location_id, name, origin, values, bom
        )

        aa = src = dest = False

        if values.get("group_id"):
            # Get locations from SO
            so = values["group_id"].sale_id

            if so:
                src = dest = self._get_procurement_location(so)
                aa = so.analytic_account_id
            else:
                # Get locations from preceding MO
                # We could try to decide if origin is MO by its name, but it
                # would be inaccurate when using custom naming sequence
                mo = self.env["mrp.production"].search([("name", "=", origin)])

                if mo:
                    src = mo.location_src_id
                    dest = mo.location_dest_id

        if aa:
            res["analytic_account_id"] = aa.id

        if src:
            res["location_src_id"] = src.id
            res["location_dest_id"] = dest.id

        return res

    def _get_procurement_location(self, sale_order):
        aa = sale_order.analytic_account_id
        location = False

        # The module sale_order_project_location_in_header adds the
        # field stock_location_id to sale order
        if hasattr(sale_order, "stock_location_id") and sale_order.stock_location_id:
            # If SO has a specific location, use it
            location = sale_order.stock_location_id
        elif aa:
            # If SO has no specific location, use project default
            location = aa.default_location_id

        return location
