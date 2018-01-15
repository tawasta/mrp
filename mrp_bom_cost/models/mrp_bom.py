# -*- coding: utf-8 -*-
from openerp import api, fields, models
import openerp.addons.decimal_precision as dp
from datetime import datetime


class MrpBom(models.Model):

    _inherit = "mrp.bom"

    @api.model
    def cron_compute_bom_cost(self):
        ''' Triggered by a scheduled action to calculate all BOMs' costs '''
        for bom in self.search([]):
            bom.component_cost = self.calculate_component_cost(bom)
            bom.cost_updated = datetime.now()

    @api.multi
    def action_compute_bom_cost(self):
        ''' Triggered by a button to calculate a single BOM's cost '''
        for bom in self:
            component_cost = self.sudo().calculate_component_cost(bom)
            updated = datetime.now()
            self.sudo().write({
                'component_cost': component_cost,
                'cost_updated': updated
            })


    def calculate_component_cost(self, bom):
        ''' Calculate costs for the BOM and its lines '''
        mrp_bom_model = self.env["mrp.bom"]
        cost = 0.0

        for line in bom.bom_line_ids:
            if line.child_bom_id:
                # If line's product has a BOM, call this function recursively until whole line cost is calculated.
                component_cost = mrp_bom_model.calculate_component_cost(line.child_bom_id)
            else:
                # If the product does not have a BOM, add the cost price of the product to the BOM costs                
                component_cost = line.calculate_component_cost()[0]

            # Update cost shown on the line
            line.component_cost = component_cost

            # Multiply line cost with product qty and add it to BOM cost
            cost += line.product_qty * component_cost 

        return cost

    @api.multi
    def _get_currency_id(self):
        try:
            main_company = self.sudo().env.ref('base.main_company')
        except ValueError:
            main_company = self.env['res.company'].sudo().search([], limit=1, order="id")
        for bom in self:
            bom.currency_id = bom.company_id.sudo().currency_id.id or main_company.currency_id.id

    component_cost = fields.Float(digits=dp.get_precision('Product Price'), string="Component Cost", help='''Contains the combined component costs of all sub-assemblies''')
    cost_updated = fields.Datetime(string="Cost updated", help="Last time BOM cost was updated.")
    currency_id = fields.Many2one('res.currency', compute=_get_currency_id, string='Currency')