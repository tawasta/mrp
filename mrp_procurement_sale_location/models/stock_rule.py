from odoo import models


class StockRule(models.Model):
    _inherit = "stock.rule"

    def _get_stock_move_values(self):
        # Override the procurement rule location with
        # sale order analytic account location

        res = super(StockRule, self)._get_stock_move_values()

        if self.sale_line_id:
            sale_order = self.sale_line_id.order_id

            location = self._get_procurement_location(sale_order)

            if location:
                res["location_id"] = location.id

        return res

    def _prepare_mo_vals(self, bom):
        # Override the MO source and destination location with
        # sale order analytic account location

        result = super(StockRule, self)._prepare_mo_vals(bom=bom)

        if self.group_id:
            sale_order = self.env["sale.order"].search(
                [("name", "=", self.group_id.name)]
            )

            location = self._get_procurement_location(sale_order)
            project = sale_order.project_id

            if location and project:
                result["analytic_account_id"] = project.id
                result["location_src_id"] = location.id
                result["location_dest_id"] = location.id

        return result

    def _get_procurement_location(self, sale_order):
        project = sale_order.project_id
        location = False

        # The module sale_order_project_location_in_header adds the
        # field stock_location_id to sale order
        if hasattr(sale_order, "stock_location_id") and sale_order.stock_location_id:
            # If SO has a specific location, use it
            location = sale_order.stock_location_id
        elif project:
            # If SO has no specific location, use project default
            location = project.default_location_id

        return location
