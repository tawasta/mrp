##############################################################################
#
#    Author: Oy Tawasta OS Technologies Ltd.
#    Copyright 2022- Oy Tawasta OS Technologies Ltd. (https://tawasta.fi)
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
import logging

# 2. Known third party imports:
# 3. Odoo imports (openerp):
from odoo import fields, models

# 4. Imports from Odoo modules:

# 5. Local imports in the relative form:

# 6. Unknown third party imports:

_logger = logging.getLogger(__name__)


class MrpBom(models.Model):
    # 1. Private attributes
    _inherit = "mrp.bom"

    # 2. Fields declaration
    bom_rel_purchase_count = fields.Integer(
        string="Reserved Purchase Quantity",
        compute="_compute_bom_rel_purchase_and_sold_count",
    )

    bom_rel_sold_count = fields.Integer(
        string="Reserved Sale Quantity",
        compute="_compute_bom_rel_purchase_and_sold_count",
    )

    # 3. Default methods

    # 4. Compute and search fields, in the same order that fields declaration
    def _compute_bom_rel_purchase_and_sold_count(self):
        for bom in self:
            product_id = self._context.get("active_id")
            product_model = self._context.get("active_model")
            if (
                product_model == "product.template"
                and product_id == bom.product_tmpl_id.id
            ) or (
                product_model == "product.product"
                and (
                    product_id == bom.product_id.id
                    or product_id == bom.product_tmpl_id.id
                )
            ):
                if product_model == "product.template":
                    product = bom.product_tmpl_id.product_variant_id
                else:
                    product = bom.product_id or bom.product_tmpl_id.product_variant_id
                stock_moves = self.env["stock.move"].search(
                    [
                        ("product_id", "=", product.id),
                        ("picking_id.state", "in", ["confirmed", "assigned"]),
                    ]
                )
                _logger.debug(
                    "Searching BoM rel counts for %s from %s." % (product, stock_moves)
                )
                bom.bom_rel_purchase_count = sum(
                    x.reserved_availability for x in stock_moves if x.purchase_line_id
                )
                bom.bom_rel_sold_count = sum(
                    x.reserved_availability for x in stock_moves if x.sale_line_id
                )
            else:
                _logger.debug(
                    "No product associated with %s." % (bom),
                )
                bom.bom_rel_purchase_count = 0
                bom.bom_rel_sold_count = 0

    # 5. Constraints and onchanges

    # 6. CRUD methods

    # 7. Action methods

    # 8. Business methods
