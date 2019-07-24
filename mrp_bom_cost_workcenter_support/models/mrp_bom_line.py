# -*- coding: utf-8 -*-
from odoo import api, fields, models


class MrpBomLine(models.Model):
    _inherit = "mrp.bom.line"

    @api.multi
    def _get_op_costs(self):
        """ Calculate for the line the related BOM's operation cost """
        for line in self:
            line.op_cost = line.child_bom_id.op_cost
            line.op_cost_total = line.op_cost * line.product_qty

    op_cost = fields.Float(
        compute=_get_op_costs,
        string='Operation Cost per Unit'
    )
    op_cost_total = fields.Float(
        compute=_get_op_costs,
        string='Total Operation Cost'
    )
