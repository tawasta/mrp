import logging
import timeit

from odoo import api, models

logger = logging.getLogger(__name__)


class MrpMultiLevel(models.TransientModel):
    _inherit = "mrp.multi.level"

    @api.model
    def _low_level_code_calculation(self):
        start = timeit.default_timer()
        logger.info("Start low level code calculation")
        llc_history = []
        counter = 999999
        llc = 0
        # Same limit as mrp_multi_level: core does not prevent every BoM cycle
        llc_recursion_limit = (
            int(
                self.env["ir.config_parameter"]
                .sudo()
                .get_param("mrp_multi_level.llc_calculation_recursion_limit")
            )
            or 20
        )
        product_model = self.env["product.product"]
        # The raw SQL below must not be overwritten by pending ORM writes
        product_model.flush_model(["llc"])

        # Every product found here gets its level in the update loop below.
        # Products not found here (archived or hidden by record rules) keep
        # their level.
        products = product_model.search([])  # pylint: disable=W8163
        if products:
            counter = len(products)
            llc_history.append((llc, products))

        log_msg = f"Low level code 0 finished - Nbr. products: {counter}"
        logger.info(log_msg)

        while counter:
            llc += 1
            products = llc_history[-1][1]
            p_templates = products.mapped("product_tmpl_id")
            bom_lines = self.env["mrp.bom.line"].search(
                [
                    ("product_id", "in", products.ids),
                    ("bom_id.product_tmpl_id", "in", p_templates.ids),
                ]
            )
            products = bom_lines.mapped("product_id")

            if products:
                llc_history.append((llc, products))

            counter = len(products)
            log_msg = f"Low level code {llc} finished - Nbr. products: {counter}"
            logger.info(log_msg)
            if llc > llc_recursion_limit:
                logger.error("Recursion limit reached during LLC calculation.")
                break

        handled_products = product_model

        for data in reversed(llc_history):
            llc_val = data[0]
            diff = data[1] - handled_products
            if diff:
                update_query = """
                    UPDATE product_product SET llc = {} WHERE id in ({})
                """.format(llc_val, ",".join(str(i) for i in diff.ids))
                logger.info(f"LLC: {llc_val}, counter: {len(diff)}")
                self.env.cr.execute(update_query)  # pylint: disable=E8103
                handled_products |= diff

        mrp_lowest_llc = llc
        exec_time = timeit.default_timer() - start
        logger.info(f"End low level code calculation, took {exec_time:.2f} seconds")
        return mrp_lowest_llc
