# -*- coding: utf-8 -*-
from openerp import models, fields, api, _, exceptions


class MrpBomLine(models.Model):

    _inherit = 'mrp.bom.line'

    @api.multi
    def _get_product_seller_ids(self):
        for bom_line in self:
            bom_line.product_seller_ids = [x.id for x in bom_line.product_id.seller_ids]

    # Use a computed many2many field instead of a related one2many to utilize the many2many_tags widget in the BOM line tree
    product_seller_ids = fields.Many2many(compute=_get_product_seller_ids, comodel_name='product.supplierinfo', relation='bom_line_supplierinfo_rel',
        column1='mrp_bom_line_id', column2='supplierinfo_id', string='Product Vendors', readonly=True)