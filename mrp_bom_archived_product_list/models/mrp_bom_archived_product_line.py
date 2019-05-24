from odoo import models, fields


class MrpBomArchivedProductLine(models.Model):

    _name = 'mrp_bom_archived_product_list.archived_product_line'

    # Create a separate class so that we can also identify the parent of the
    # archived product in the BOM
    bom_id = fields.Many2one(
        comodel_name='mrp.bom',
        string='Main BOM',
    )

    parent_id = fields.Many2one(
        comodel_name='mrp.bom',
        string='Parent BOM',
    )

    product_id = fields.Many2one(
        comodel_name='product.product',
        string='Product',
    )
