# -*- coding: utf-8 -*-
from openerp import api, fields, models
import openerp.addons.decimal_precision as dp


class MrpBomLine(models.Model):

    _inherit = "mrp.bom.line"

    @api.one
    def calculate_component_cost(self):
        ''' Returns the cost of the BOM line. By default fetches the cost from the 
        cost price field of the related product. Override this function for more 
        complex calculations. '''
        cost = self.product_id.standard_price
        return cost

    @api.multi
    def _get_component_cost_total(self):
        for line in self:
            line.component_cost_total = line.component_cost * line.product_qty

    component_cost = fields.Float(string="Component Cost (individual)", digits=dp.get_precision('Product Price'), help='''Component cost for 1 BOM line item''')
    component_cost_total = fields.Float(compute=_get_component_cost_total, string="Component Cost (total)", digits=dp.get_precision('Product Price'), help='''Component cost for the full quantity of the BOM line's item''')