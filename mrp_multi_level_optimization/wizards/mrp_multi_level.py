import timeit
from odoo import api, models
import logging
logger = logging.getLogger(__name__)


class MrpMultiLevel(models.TransientModel):

    _inherit = 'mrp.multi.level'

    @api.model
    def _low_level_code_calculation(self):
        start = timeit.default_timer()
        logger.info('Start low level code calculation')
        llc_history = []
        counter = 999999
        llc = 0

        select_query = """
            UPDATE product_product SET llc = {}
        """.format(llc)

        self.env.cr.execute(select_query)

        products = self.env['product.product'].search([])
        if products:
            counter = len(products)
            llc_history.append((llc, products))

        log_msg = 'Low level code 0 finished - Nbr. products: %s' % counter
        logger.info(log_msg)

        while counter:
            llc += 1
            products = llc_history[-1][1]
            p_templates = products.mapped('product_tmpl_id')
            bom_lines = self.env['mrp.bom.line'].search(
                [('product_id', 'in', products.ids),
                 ('bom_id.product_tmpl_id', 'in', p_templates.ids)])
            products = bom_lines.mapped('product_id')

            if products:
                llc_history.append((llc, products))

            counter = len(products)
            log_msg = 'Low level code %s finished - Nbr. products: %s' % (
                llc, counter)
            logger.info(log_msg)

        handled_products = self.env['product.product']
        for data in reversed(llc_history):
            llc_val = data[0]
            diff = data[1] - handled_products
            if diff:
                update_query = """
                    UPDATE product_product SET llc = {} WHERE id in ({})
                """.format(llc_val, ','.join(str(i) for i in diff.ids))
                logger.info("LLC: {}, counter: {}".format(llc_val, len(diff)))
                self.env.cr.execute(update_query)
                handled_products |= diff

        mrp_lowest_llc = llc
        exec_time = timeit.default_timer() - start
        logger.info('End low level code calculation, took {:.2f} seconds'.format(exec_time))
        return mrp_lowest_llc
