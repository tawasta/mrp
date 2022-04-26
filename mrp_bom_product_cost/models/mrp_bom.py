from odoo import _, api, fields, models
import odoo.addons.decimal_precision as dp
from datetime import datetime
from odoo.addons.queue_job.job import job
import logging

_logger = logging.getLogger(__name__)


class MrpBom(models.Model):

    _inherit = "mrp.bom"

    @api.multi
    @job
    def _cron_compute_bom_cost(self, boms):
        for bom in boms:
            bom.component_cost = self.calculate_component_cost(bom)
            bom.cost_updated = datetime.now()

    @api.multi
    @job
    def cron_compute_bom_cost(self):
        """ Triggered by a scheduled action to calculate all BOMs' costs """
        boms = self.search([])

        batch_boms = list()
        interval = 50
        for x in range(0, len(boms), interval):
            batch_boms.append(boms[x:x+interval])

        for batch in batch_boms:
            job_desc = _(
                "Assign values to BoMs: {}".format(batch)
            )
            self.with_delay(
                description=job_desc)._cron_compute_bom_cost(batch)

        _logger.info("Cron for Compute BoM cost completed")

    @api.multi
    def action_compute_bom_cost(self):
        """ Triggered by a button to calculate a single BOM's cost """
        for bom in self:
            component_cost = self.sudo().calculate_component_cost(bom)
            updated = datetime.now()
            self.sudo().write({
                'component_cost': component_cost,
                'cost_updated': updated
            })

    def calculate_component_cost(self, bom):
        """ Calculate costs for the BOM and its lines """
        mrp_bom_model = self.env["mrp.bom"]
        cost = 0.0

        for line in bom.bom_line_ids:
            if line.child_bom_id:
                # If line's product has a BOM, call this function recursively
                # until whole line cost is calculated.
                component_cost \
                    = mrp_bom_model.calculate_component_cost(line.child_bom_id)
            else:
                # If the product does not have a BOM,
                # add the cost price of the product to the BOM costs
                component_cost = line.calculate_component_cost()

            # Update cost shown on the line
            line.component_cost = component_cost

            # Multiply line cost with product qty and add it to BOM cost
            cost += line.product_qty * component_cost

        cost = cost / bom.product_qty

        return cost

    @api.multi
    def _get_currency_id(self):
        try:
            main_company = self.sudo().env.ref('base.main_company')
        except ValueError:
            main_company = self.env['res.company'].sudo().search(
                [],
                limit=1,
                order="id"
            )
        for bom in self:
            bom.currency_id = bom.company_id.sudo().currency_id.id \
                or main_company.currency_id.id

    component_cost = fields.Float(
        digits=dp.get_precision('Product Price'),
        string="Unit Component Cost",
        help="Contains the combined component cost of all sub-assemblies, "
             "for one produced unit",
    )

    cost_updated = fields.Datetime(
        string="Cost updated",
        help="Last time BOM cost was updated."
    )

    currency_id = fields.Many2one(
        comodel_name='res.currency',
        compute=_get_currency_id,
        string='Currency'
    )
