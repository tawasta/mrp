##############################################################################
#
#    Author: Oy Tawasta OS Technologies Ltd.
#    Copyright 2021- Oy Tawasta OS Technologies Ltd. (https://tawasta.fi)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program. If not, see http://www.gnu.org/licenses/agpl.html
#
##############################################################################

# 1. Standard library imports:

# 2. Known third party imports:

# 3. Odoo imports (openerp):
from odoo import fields, models, api
from odoo.addons import decimal_precision as dp

# 4. Imports from Odoo modules:

# 5. Local imports in the relative form:

# 6. Unknown third party imports:


class MrpProduction(models.Model):

    # 1. Private attributes
    _inherit = 'mrp.production'

    # 2. Fields declaration
    product_qty = fields.Float(
        'Quantity To Produce',
        default=1.0, digits=dp.get_precision('Product Unit of Measure'),
        readonly=True, required=True, track_visibility='onchange',
        states={'confirmed': [('readonly', False)]},
        compute='_compute_qty_multiplied'

    )

    product_qty_multiplier = fields.Float(
        'Multiplier for Quantity',
        default=1.0, digits=dp.get_precision('Product Unit of Measure'),
        readonly=True, required=True, track_visibility='onchange',
        states={'confiurmed': [('readonly', False)]},

    )

    # 3. Default methods

    # 4. Compute and search fields, in the same order that fields declaration
    @api.depends('product_qty_multiplier')
    def _compute_qty_multiplied(self):
        for production in self:
            print("COMPUTE")
            print(production.product_qty_multiplier)
            print(production.product_qty)
            if production.product_qty_multiplier >= 1:
                production.product_qty = production.product_qty * production.product_qty_multiplier

    # 5. Constraints and onchanges
    # @api.onchange('product_qty', 'product_qty_multiplier')
    # def onchange_product_qty_multiplied(self):
    #     print("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")
    #     print("00000000000000000000000000000000000000000000000000000000000000000")
    #     if self.product_qty_multiplier >= 1:
    #         self.product_qty = self.product_qty * self.product_qty_multiplier

    # 6. CRUD methods
    # @api.model
    # def create(self, values):
    #     production = super(MrpProduction, self).create(values)
    #     print("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")
    #     print(production['product_qty'])
    #     print(production['product_qty_multiplied'])
    #     production['product_qty'] = production['product_qty'] * production['product_qty_multiplier']
    #     return production

    # 7. Action methods

    # 8. Business methods
