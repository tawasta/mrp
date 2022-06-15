
from odoo import api, fields, models


class MrpInventory(models.Model):

    _inherit = 'mrp.inventory'

    @api.model
    def create(self, vals):
        param = self.env['product.mrp.area'].search(
            [('id', '=', vals.get('product_mrp_area_id'))])
        product = param.product_id

        if product.sh_product_tag_ids:
            vals['sh_product_tag_ids'] = ','.join(
                    [p.name for p in product.sh_product_tag_ids])
        else:
            vals['sh_product_tag_ids'] = ''
        return super().create(vals)

    sh_product_tag_ids = fields.Char(string='Tags')
