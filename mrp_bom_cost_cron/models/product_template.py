import logging

from odoo import _, models

_logger = logging.getLogger(__name__)


class ProductTemplate(models.Model):

    _inherit = "product.template"

    def _cron_button_bom_cost(self, batch):
        prods = self.env["product.template"].search([("id", "in", batch)])
        for prod in prods:
            prod.button_bom_cost()
        return batch, "Success"

    def cron_button_bom_cost(self):
        """Computes compute cost for each product"""

        multi_level_installed = self.env["ir.module.module"].search(
            [("name", "=", "mrp_multi_level")]
        )
        multi_level_installed = (
            multi_level_installed and multi_level_installed.state == "installed"
        )

        products = self.env["product.template"].search([("bom_ids", "!=", False)])

        # Use llc-field if it exists in the installation
        if multi_level_installed and "llc" in self.env["product.product"]._fields:
            products = products.sorted(
                key=lambda p: p.product_variant_id.llc, reverse=True
            )

        products = products.ids

        batch_products = list()
        interval = 50
        for x in range(0, len(products), interval):
            batch_products.append(products[x : x + interval])

        for batch in batch_products:
            job_desc = _("Update component cost for products: {}").format(batch)
            self.with_delay(description=job_desc)._cron_button_bom_cost(batch)

        _logger.info("Cron Compute component cost completed")
