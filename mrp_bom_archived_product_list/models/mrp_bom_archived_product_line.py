# -*- coding: utf-8 -*-
from openerp import models, fields, api, _, exceptions


class MrpBomArchivedProductLine(models.Model):

    _name = 'mrp_bom_archived_product_list.archived_product_line'

    # Create a separate class so that we can also identify the parent of the archived product in the BOM
    bom_id = fields.Many2one('mrp.bom', 'Main BOM')
    parent_id = fields.Many2one('mrp.bom', 'Parent BOM')    
    product_id = fields.Many2one('product.product', 'Product')
