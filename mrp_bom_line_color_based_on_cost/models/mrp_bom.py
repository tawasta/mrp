
from odoo import api, fields, models


class MrpBom(models.Model):

    _inherit = 'mrp.bom'

    bom_line_vendor_price_is_zero = fields.Boolean(
        compute="_compute_bom_line_vendor_price_is_zero")

    @api.depends("bom_line_ids.primary_vendor_price")
    def _compute_bom_line_vendor_price_is_zero(self):
        for bom in self:
            if any(line for line in bom.bom_line_ids if
                   line.primary_vendor_price == 0 and
                   line.primary_vendor_uom_id or not
                   line.primary_vendor_uom_id):
                bom.bom_line_vendor_price_is_zero = True
            else:
                bom.bom_line_vendor_price_is_zero = False
