from odoo import api, fields, models, _
from itertools import groupby

import logging

_logger = logging.getLogger(__name__)


class ProductProduct(models.Model):
    _inherit = "product.product"

    llc = fields.Integer(string="Low Level Code", default=0)

    def _cron_button_bom_cost(self, batch):
        prods = self.env["product.product"].search([("id", "in", batch)])
        for prod in prods:
            prod.button_bom_cost()
        return batch, "Success"

    def cron_button_bom_cost_after_llc_computation(self):
        """Computes compute cost for each product"""

        # Note that sorting is done in reverse and based on llc-values.
        # Bigger llc-values means that a product is on a lower level
        # in the BoM-hierarchy.
        products = (
            self.env["product.product"]
            .search([("bom_ids", "!=", False)])
            .sorted(key=lambda p: p.llc, reverse=True)
        )

        if products:
            products_and_llc = [(p.llc, p.id) for p in products]
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
                job_desc = _(
                    "Update component cost for products {} with llc {}"
                ).format(batch, llc)
                self.with_delay(
                    description=job_desc, priority=priority
                )._cron_button_bom_cost(batch)
                priority += 1
        _logger.info("Cron Compute component cost completed")

    def get_products(self, llc):
        for product in self.env["product.product"].search([("llc", "=", llc)]):
            yield product

    @api.model
    def _low_level_code_calculation(self):
        _logger.info("Start low level code calculation")
        counter = 999999
        llc = 0

        select_query = """
            UPDATE product_product SET llc = {}
        """.format(llc)

        self.env.cr.execute(select_query)

        products = self.env["product.product"].search([("llc", "=", llc)])
        if products:
            counter = len(products)
        log_msg = "Low level code 0 finished - Nbr. products: %s" % counter
        _logger.info(log_msg)

        while counter:
            llc += 1
            products = self.get_products(llc - 1)
            p_templates = [x.product_tmpl_id.id for x in products]
            bom_lines = self.env["mrp.bom.line"].search(
                [
                    ("product_id.llc", "=", llc - 1),
                    ("bom_id.product_tmpl_id", "in", p_templates),
                ]
            )
            products = bom_lines.mapped("product_id")

            select_query = """
                UPDATE product_product SET llc = {} WHERE id in ({})
            """.format(llc, ",".join(str(i) for i in products.ids))

            if products:
                self.env.cr.execute(select_query)

            products = self.get_products(llc)
            counter = len(list(products))

            log_msg = "Low level code %s finished - Nbr. products: %s" % (llc, counter)
            _logger.info(log_msg)

        _logger.info("End low level code calculation")
        job_desc = "Computes compute cost for each product"

        self.with_delay(
            description=job_desc
        ).cron_button_bom_cost_after_llc_computation()

    def cron_button_bom_cost(self):
        job_desc = "Compute LLC values"

        self.with_delay(description=job_desc)._low_level_code_calculation()
