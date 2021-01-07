from odoo import api, models
import logging
logger = logging.getLogger(__name__)


class MrpMultiLevel(models.TransientModel):

    _inherit = 'mrp.multi.level'

    def get_products(self, llc):
        for product in self.env['product.product'].search([('llc', '=', llc)]):
            yield product

    @api.model
    def _low_level_code_calculation(self):
        logger.info('Start low level code calculation')
        counter = 999999
        llc = 0

        select_query = """
            UPDATE product_product SET llc = {}
        """.format(llc)

        self.env.cr.execute(select_query)

        products = self.env['product.product'].search([('llc', '=', llc)])
        if products:
            counter = len(products)
        log_msg = 'Low level code 0 finished - Nbr. products: %s' % counter
        logger.info(log_msg)

        while counter:
            llc += 1
            products = self.get_products(llc - 1)
            p_templates = [x.product_tmpl_id.id for x in products]
            bom_lines = self.env['mrp.bom.line'].search(
                [('product_id.llc', '=', llc - 1),
                 ('bom_id.product_tmpl_id', 'in', p_templates)])
            products = bom_lines.mapped('product_id')

            select_query = """
                UPDATE product_product SET llc = {} WHERE id in ({})
            """.format(llc, ','.join(str(i) for i in products.ids))

            if products:
                self.env.cr.execute(select_query)

            products = self.get_products(llc)
            counter = len(list(products))

            log_msg = 'Low level code %s finished - Nbr. products: %s' % (
                llc, counter)
            logger.info(log_msg)

        mrp_lowest_llc = llc
        logger.info('End low level code calculation')
        return mrp_lowest_llc
