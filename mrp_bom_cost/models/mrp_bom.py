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
            bom.bom_cost = self.calculate_cost(bom)
            bom.cost_updated = datetime.now()

    @api.multi
    def action_compute_bom_cost(self):
        ''' Triggered by a button to calculate a single BOM's cost '''
        for bom in self:
            bom_cost = self.sudo().calculate_cost(bom)
            updated = datetime.now()
            self.sudo().write({
                'bom_cost': bom_cost,
                'cost_updated': updated
            })


    def calculate_cost(self, bom):
        ''' Calculate costs for the BOM and its lines '''
        mrp_bom_model = self.env["mrp.bom"]
        cost = 0.0

        for line in bom.bom_line_ids:
            if line.child_bom_id:
                # If line's product has a BOM, call this function recursively until whole line cost is calculated.
                line_cost = mrp_bom_model.calculate_cost(line.child_bom_id)
            else:
                # If the product does not have a BOM, add the cost price of the product to the BOM costs                
                line_cost = line.calculate_line_cost()[0]

            # Update cost shown on the line
            line.line_cost = line_cost

            # Multiply line cost with product qty and add it to BOM cost
            cost += line.product_qty * line_cost 

        return cost

    bom_cost = fields.Float(digits=dp.get_precision('Product Price'), string="BOM Component Cost")
    cost_updated = fields.Datetime(string="Cost updated", help="Last time BOM cost was updated.")