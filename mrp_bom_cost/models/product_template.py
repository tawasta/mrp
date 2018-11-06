# -*- coding: utf-8 -*-
from odoo import fields, models
import openerp.addons.decimal_precision as dp


class ProductTemplate(models.Model):

    _inherit = 'product.template'

    def _compute_bom_component_cost(self):
        bom_model = self.env['mrp.bom']
        for product in self:
            bom_id = bom_model._bom_find(product_tmpl=product)
            product.bom_component_cost \
                = bom_id and bom_id.component_cost or 0.00

    bom_component_cost = fields.Float(
        digits=dp.get_precision('Product Price'),
        compute=_compute_bom_component_cost,
        string="BOM Component Cost",
        help="The combined component costs of BOM's sub-assemblies"
    )
