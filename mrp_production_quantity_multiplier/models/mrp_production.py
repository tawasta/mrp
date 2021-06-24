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
import math

# 2. Known third party imports:

# 3. Odoo imports (openerp):
from odoo import fields, models, api

# 4. Imports from Odoo modules:

# 5. Local imports in the relative form:

# 6. Unknown third party imports:


class MrpProduction(models.Model):

    # 1. Private attributes
    _inherit = 'mrp.production'

    # 2. Fields declaration
    product_qty_multiplier = fields.Integer(
        'Multiplier for Quantity',
        default=1,
    )

    # 3. Default methods

    # 4. Compute and search fields, in the same order that fields declaration

    # 5. Constraints and onchanges
    @api.onchange('bom_id', 'product_qty_multiplier')
    def onchange_product_qty_multiplied(self):
        self.product_qty = self.bom_id.product_qty * (self.product_qty_multiplier or 1)

    # 6. CRUD methods
    @api.model
    def create(self, values):
        bom = self.env['mrp.bom'].search([('id', '=', values.get('bom_id'))])
        multiply_by = math.ceil(values.get('product_qty') / bom.product_qty)
        values['product_qty'] = multiply_by * bom.product_qty
        return super(MrpProduction, self).create(values)

    # 7. Action methods

    # 8. Business methods
