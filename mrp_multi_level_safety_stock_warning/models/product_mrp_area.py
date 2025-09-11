
from odoo import api, fields, models


class ProductMrpArea(models.Model):

    _inherit = 'product.mrp.area'

    safety_stock_warning = fields.Boolean(
        string="More Qty needed",
        compute=lambda self: self._compute_safety_stock_warning(),
    )

    @api.depends('mrp_minimum_stock', 'qty_available')
    def _compute_safety_stock_warning(self):
        for prod_area in self:
            if prod_area.mrp_minimum_stock > prod_area.qty_available:
                prod_area.safety_stock_warning = True
            else:
                prod_area.safety_stock_warning = False
