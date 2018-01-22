# -*- coding: utf-8 -*-

from odoo import api, fields, models


class ProcurementOrder(models.Model):
    _inherit = 'procurement.order'

    '''
    @api.model
    def create(self, values):
        if 'sale_line_id' in values:
            sale_order_line = self.env['sale.order.line'].browse([
                values['sale_line_id']
            ])
            sale_order = sale_order_line.order_id

            if sale_order.project_id and sale_order.project_id.location_ids:
                values['location_id'] = \
                sale_order_line.order_id.project_id.default_location_id.id

        return super(ProcurementOrder, self).create(values)
    '''

    def _prepare_mo_vals(self, bom):
        result = super(ProcurementOrder, self)._prepare_mo_vals(bom=bom)

        if self.group_id:
            sale_order = self.env['sale.order'].search([
                ('name', '=', self.group_id.name),
            ])

            if sale_order.project_id and \
                    sale_order.project_id.default_location_id:

                location = sale_order.project_id.default_location_id
                result['analytic_account_id'] = sale_order.project_id.id
                result['location_src_id'] = location.id
                result['location_dest_id'] = location.id

        return result