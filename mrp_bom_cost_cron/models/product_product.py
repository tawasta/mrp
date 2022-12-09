
from odoo import api, fields, models, _
from odoo.addons.queue_job.job import job
import logging
_logger = logging.getLogger(__name__)


class ProductProduct(models.Model):

    _inherit = 'product.product'

    llc = fields.Integer(string='Low Level Code', default=0)

    @api.multi
    @job
    def _cron_button_bom_cost(self, batch):
        prods = self.env['product.product'].search([('id', 'in', batch)])
        for prod in prods:
            # The function below is used so that it will work with products
            # with FIFO valuation. button_bom_cost()-function is not used
            # because with FIFO valuation it will try to open a form view
            # which would do nothing here.
            prod.standard_price = prod._get_price_from_bom()
        return batch, 'Success'

    @api.multi
    @job
    def cron_button_bom_cost_after_llc_computation(self):
        """ Computes compute cost for each product """

        # Note that sorting is done in reverse and based on llc-values.
        # Bigger llc-values means that a product is on a lower level
        # in the BoM-hierarchy.
        products = self.env['product.product'].search(
            [('bom_ids', '!=', False)]).sorted(
                    key=lambda p: p.llc, reverse=True).ids

        batch_products = list()
        interval = 50
        for x in range(0, len(products), interval):
            batch_products.append(products[x:x+interval])

        for batch in batch_products:
            job_desc = _(
                "Update component cost for products: {}".format(batch)
            )
            self.with_delay(
                description=job_desc)._cron_button_bom_cost(batch)

        _logger.info("Cron Compute component cost completed")

    def get_products(self, llc):
        for product in self.env['product.product'].search([('llc', '=', llc)]):
            yield product

    @api.model
    @job
    def _low_level_code_calculation(self):
        _logger.info('Start low level code calculation')
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
        _logger.info(log_msg)

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
            _logger.info(log_msg)

        mrp_lowest_llc = llc
        _logger.info('End low level code calculation')

        job_desc = "Computes compute cost for each product"

        self.with_delay(
            description=job_desc).cron_button_bom_cost_after_llc_computation()

    @api.multi
    @job
    def cron_button_bom_cost(self):
        job_desc = "Compute LLC values"

        self.with_delay(
            description=job_desc)._low_level_code_calculation()
