# -*- coding: utf-8 -*-

from odoo import api, fields, models


class ProcurementOrder(models.Model):
    _inherit = 'procurement.order'

    def _get_stock_move_values(self):
        # Override the procurement rule location with
        # sale order analytic account location

        res = super(ProcurementOrder, self)._get_stock_move_values()

        if self.sale_line_id:
            sale_order = self.sale_line_id.order_id
            project = sale_order.project_id

            if project and project.default_location_id:
                res['location_id'] = project.default_location_id.id

        return res

    def _prepare_mo_vals(self, bom):
        # Override the MO source and destination location with
        # sale order analytic account location

        result = super(ProcurementOrder, self)._prepare_mo_vals(bom=bom)

        if self.group_id:
            sale_order = self.env['sale.order'].search([
                ('name', '=', self.group_id.name),
            ])

            if sale_order:
                project = sale_order.project_id

                if hasattr(sale_order, 'stock_location_id'):
                    location = sale_order.stock_location_id
                else:
                    location = project.default_location_id

                if project and location:

                    result['analytic_account_id'] = project.id
                    result['location_src_id'] = location.id
                    result['location_dest_id'] = location.id

        return result
