
from odoo import fields, models


class MrpBom(models.Model):

    _inherit = 'mrp.bom'

    bom_rel_count = fields.Integer(
        string="Total product count",
        compute="_compute_bom_rel_count"
    )

    bom_rel_available_count = fields.Integer(
        string="On Hand",
        compute="_compute_bom_rel_count"
    )

    def _compute_bom_rel_count(self):
        product_id = self._context.get('active_id')
        product_model = self._context.get('active_model')
        if product_model in ['product.product', 'product.template']:
            product = self.env[product_model].search([('id', '=', product_id)])
            product = product.product_variant_id or product
            bom_lines = self.env['mrp.bom.line'].search(
                [('product_id', '=', product.id)]
            )
            for line in bom_lines:
                line.bom_id.bom_rel_count = line.product_qty
                line.bom_id.bom_rel_available_count = line.product_id.qty_available
