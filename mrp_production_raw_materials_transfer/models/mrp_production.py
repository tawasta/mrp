# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import RedirectWarning


class MrpProduction(models.Model):

    _inherit = 'mrp.production'


    def _get_picking_type_for_transfer(self):
        if not self.company_id.raw_materials_picking_type_id:
            action = self.env.ref('mrp.action_mrp_configuration')
            msg = _('Internal transfer picking type unconfigured. \nPlease go to MRP Configuration.')
            # TODO: why doesn't the warning show the link to MRP configuration?
            raise RedirectWarning(msg, action.id, _('Go to the configuration panel'))
        else:
            return self.company_id.raw_materials_picking_type_id.id

    def _get_source_location_for_transfer(self):
        if not self.company_id.raw_materials_src_location_id:
            action = self.env.ref('mrp.action_mrp_configuration')
            msg = _('Default Source location unconfigured. \nPlease go to MRP Configuration.')
            # TODO: why doesn't the warning show the link to MRP configuration?
            raise RedirectWarning(msg, action.id, _('Go to the configuration panel'))
        else:
            return self.company_id.raw_materials_src_location_id.id

    @api.multi
    def create_raw_material_transfer(self):
        ''' Creates a new stock picking for transfering raw materials
        to the current production location '''
        self.ensure_one()

        stock_picking_model = self.env['stock.picking']
        stock_move_model = self.env['stock.move']

        vals = {
            'picking_type_id': self._get_picking_type_for_transfer(),
            'location_id': self._get_source_location_for_transfer(),
            'location_dest_id': self.location_src_id.id,
            'origin': '%s %s' % (_('Raw materials for'), self.name)
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