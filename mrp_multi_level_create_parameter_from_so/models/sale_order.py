
from odoo import api, models


class SaleOrder(models.Model):

    _inherit = 'sale.order'

    def prepare_product_mrp_area_vals(self, product):
        """ Default Product Mrp Area values """
        return {
            "mrp_area_id": 1,
            "product_id": product.id,
        }

    @api.multi
    def action_confirm(self):
        """ Creates a new Product Mrp Area record if a product does not
        have it """
        res = super().action_confirm()
        product_mrp_area_model = self.env['product.mrp.area']

        # Goes through sale order lines to check if a product does not
        # have Product Mrp Area record attached to it
        for line in self.order_line:
            product = line.product_id
            # Search also archived records to avoid unique error
            parameter = product_mrp_area_model.sudo().search([
                ('product_id', '=', product.id),
                '|', ('active', '=', True), ('active', '=', False)
            ])
            if not parameter and \
                    product.type in ['consu', 'product']:
                values = self.prepare_product_mrp_area_vals(product)
                # Creates Product Mrp Area record
                product_mrp_area_model.sudo().create(values)

        return res
