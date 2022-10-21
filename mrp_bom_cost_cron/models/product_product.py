
from odoo import api, fields, models, _
from odoo.addons.queue_job.job import job
import logging
_logger = logging.getLogger(__name__)


class ProductProduct(models.Model):

    _inherit = 'product.product'

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
    def cron_button_bom_cost(self):
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
