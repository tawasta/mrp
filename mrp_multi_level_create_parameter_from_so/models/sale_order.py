
from odoo import api, models


class SaleOrder(models.Model):

    _inherit = 'sale.order'

    def prepare_product_mrp_area_vals(self, product):
        """ Default Product Mrp Area values """
        return {
            "mrp_area_id": 1,
            "product_id": product.id,
        }

    def mrp_area_search_domain(self, product):
        """ Search domain of Product Mrp Area records """

        # Search also archived records to avoid unique error
        return [('product_id', '=', product.id), '|',
                ('active', '=', True), ('active', '=', False)]

    def get_searchable_products(self, line):
        """ Inherit this function to search other products """
        return line.product_id

    @api.multi
    def action_confirm(self):
        """ Creates a new Product Mrp Area record if a product does not
        have it """
        res = super().action_confirm()
        product_mrp_area_model = self.env['product.mrp.area']

        # Goes through sale order lines to check if a product does not
        # have Product Mrp Area record attached to it
        for line in self.order_line:
            products = self.get_searchable_products(line)

            # Looping in case more products are used
            for prod in products:
                domain = self.mrp_area_search_domain(prod)
                parameters = product_mrp_area_model.sudo().search(domain)
                if not parameters and \
                        prod.type in ['consu', 'product']:
                    values = self.prepare_product_mrp_area_vals(prod)
                    # Creates Product Mrp Area record
                    product_mrp_area_model.sudo().create(values)

        return res
