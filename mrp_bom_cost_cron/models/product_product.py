
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
            prod.button_bom_cost()
        return batch, 'Success'

    @api.multi
    @job
    def cron_button_bom_cost(self):
        """ Computes compute cost for each product """
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
