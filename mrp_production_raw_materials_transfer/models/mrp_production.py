# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class MrpProduction(models.Model):

    _inherit = 'mrp.production'

    @api.multi
    def create_raw_material_transfer(self):
        ''' Creates a new stock picking for transfering raw materials
        to production location '''
        self.ensure_one()

        picking_type_model = self.env['stock.picking.type']
        stock_picking_model = self.env['stock.picking']
        stock_move_model = self.env['stock.move']

        vals = {
            'picking_type_id': picking_type_model.search(args=[('code', '=', 'internal')], limit=1).id, # FIXME proper searching
            'location_id': self.location_src_id.id,
            'location_dest_id': self.location_src_id.id,
            'origin': '%s / Raw Materials' % self.name
        }

        res = stock_picking_model.create(vals)

        for material in self.move_raw_ids:
            if not material.product_id.bom_ids:
                stock_move_model.create({
                    'name': material.product_id.name,
                    'picking_id': res.id,
                    'product_id': material.product_id.id,
                    'product_uom': material.product_uom.id,
                    'product_uom_qty': material.product_uom_qty,
                    'location_id': res.location_id.id,
                    'location_dest_id': res.location_dest_id.id,
                })

        return {
            'name': '%s / Raw Materials' % self.name,
            'view_type': 'form',
            'view_mode': 'form, tree',
            'res_model': 'stock.picking',
            'type': 'ir.actions.act_window',
            'target': 'current',
            'res_id': res.id,
        }