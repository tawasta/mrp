from odoo import models, api


class ProductSupplierinfo(models.Model):

    _inherit = "product.supplierinfo"

    @api.multi
    def name_get(self):
        # Customized name_get() that can show either just the name,
        # or name + vendor code + vendor price,
        # depending on the passed context parameter.

        res = []
        show_code_and_price = self.env.context.get("show_code_and_price", False)

        for supplierinfo in self:
            if show_code_and_price:
                # E.g. "Vendor Inc (PC-0001) - 25€"
                name = u"{} ({}) - {}{}".format(
                    supplierinfo.name.name,
                    supplierinfo.product_code,
                    supplierinfo.price,
                    supplierinfo.currency_id.symbol,
                )
                res.append((supplierinfo.id, name))
            else:
                # No context parameter present,
                # so show just the name as fallback
                res.append((supplierinfo.id, supplierinfo.name.name))

        return res
