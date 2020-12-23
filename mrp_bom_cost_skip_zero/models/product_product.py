from odoo import models


class Product(models.Model):

    _inherit = "product.product"

    def button_bom_cost(self):
        # Overriding the original function is difficult
        # so need to juggle the price around
        price = self.standard_price

        res = super().button_bom_cost()

        if self.standard_price == 0:
            # Restore the original price
            self.standard_price = price

        return res

    def action_bom_cost(self):
        # Overriding the original function is difficult
        # so need to juggle the price around
        price = self.standard_price

        res = super().action_bom_cost()

        if self.standard_price == 0:
            # Restore the original price
            self.standard_price = price

        return res
