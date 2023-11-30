import logging
from itertools import groupby

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
            _logger.info("Just checking: mrp_multi_level module is installed.")
            products = products.sorted(
                key=lambda p: p.product_variant_id.llc, reverse=True
            )

        products_and_llc = [(p.product_variant_id.llc, p.id) for p in products]
        products_and_llc.sort(key=lambda x: x[0], reverse=True)

        def key_func(x):
            return x[0]

        products_and_llc = groupby(products_and_llc, key_func)

        batch_products = list()
        interval = 50

        for llc, prod in products_and_llc:
            prods = [p[1] for p in list(prod)]
            for x in range(0, len(prods), interval):
                batch_products.append((prods[x : x + interval], llc))

        priority = 0
        for batch, llc in batch_products:
            job_desc = _("Update component cost for products {} with llc {}").format(
                batch, llc
            )
            self.with_delay(
                description=job_desc, priority=priority
            )._cron_button_bom_cost(batch)
            priority += 1

        _logger.info("Cron Compute component cost completed")
