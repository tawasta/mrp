# -*- coding: utf-8 -*-
from odoo import fields, models


class ResCompany(models.Model):

    _inherit = 'res.company'

    def _get_bom_cost_calc_methods(self):
        return [('cost_price', 'Cost Price'),
                ('vendor_price', "Primary Vendor's Price")]

    bom_cost_calculation_method = fields.Selection(
        selection=_get_bom_cost_calc_methods,
        default='cost_price',
        string='BOM Cost Calculation Method',
    )
