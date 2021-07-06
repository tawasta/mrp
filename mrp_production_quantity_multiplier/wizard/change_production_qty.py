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
from odoo import models, fields, api

# 4. Imports from Odoo modules:

# 5. Local imports in the relative form:

# 6. Unknown third party imports:


class ChangeProductionQty(models.TransientModel):
    # 1. Private attributes
    _inherit = "change.production.qty"

    # 2. Fields declaration
    product_qty_multiplier = fields.Integer(
        "Multiplier for Quantity",
        help="Multiply product quantity from BoM.",
        required=True,
    )

    # 3. Default methods
    @api.model
    def default_get(self, fields):
        res = super(ChangeProductionQty, self).default_get(fields)
        if (
            "product_qty_multiplier" in fields
            and not res.get("product_qty_multiplier")
            and res.get("mo_id")
        ):
            res["product_qty_multiplier"] = (
                self.env["mrp.production"].browse(res["mo_id"]).product_qty_multiplier
            )
        return res

    # 4. Compute and search fields, in the same order that fields declaration

    # 5. Constraints and onchanges
    @api.onchange("product_qty_multiplier")
    def onchange_product_qty_multiplied(self):
        self.product_qty = self.mo_id.bom_id.product_qty * (
            self.product_qty_multiplier or 1
        )
        self.mo_id.product_qty_multiplier = (
            self.product_qty_multiplier or self.mo_id.product_qty_multiplier
        )

    # 6. CRUD methods

    # 7. Action methods
    @api.multi
    def change_prod_qty(self):
        res = super(ChangeProductionQty, self).change_prod_qty()
        for wizard in self:
            wizard.mo_id.product_qty_multiplier = (
                self.product_qty_multiplier or wizard.mo_id.product_qty_multiplier
            )
        return res

    # 8. Business methods
