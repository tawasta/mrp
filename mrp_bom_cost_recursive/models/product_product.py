from odoo import models


class Product(models.Model):

    _inherit = "product.product"

    def _compute_bom_price(self, bom, boms_to_recompute=False):
        """
        for line in bom.bom_line_ids:
            print("LINE: {}".format(line))
            print("PRODUCT: {}".format(line.product_id.name))
            line.product_id.action_bom_cost()
        """
        for line in bom.bom_line_ids:
            product = line.product_id
            if product.bom_ids:
                product.action_bom_cost()

        return super(Product, self)._compute_bom_price(bom, boms_to_recompute)
