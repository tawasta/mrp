# -*- coding: utf-8 -*-


from __future__ import division
from odoo import api, fields, models
import math


class MrpProduction(models.Model):

    _inherit = 'mrp.production'

    qty_multiple = fields.Integer(
            string='Multiple Of Qty',
            default=1,
    )

    @api.onchange('bom_id', 'qty_multiple')
    def get_quantity_from_bom(self):
        self.product_qty = self.bom_id.product_qty * \
                    (self.qty_multiple or 1)

    @api.model
    def create(self, vals):
        bom = self.env['mrp.bom'].search([('id','=',vals.get('bom_id'))])

        multiply_by = math.ceil(vals.get('product_qty') / bom.product_qty)

        vals['product_qty'] = multiply_by * bom.product_qty

        return super(MrpProduction, self).create(vals)
