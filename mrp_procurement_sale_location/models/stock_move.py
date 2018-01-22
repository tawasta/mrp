# -*- coding: utf-8 -*-

from odoo import api, fields, models


class StockMove(models.Model):
    _inherit = 'stock.move'

    '''
    def _get_new_picking_values(self):
        res = super(StockMove, self)._get_new_picking_values()

        if res['origin']:
            sale_order = self.env['sale.order'].search([
                ('name', '=', res['origin']),
            ])

            if sale_order:
                res['location_id'] = sale_order.project_id.\
                    default_location_id.id

        return res
    '''
