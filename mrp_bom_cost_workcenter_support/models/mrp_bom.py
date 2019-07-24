# -*- coding: utf-8 -*-
from odoo import api, fields, models
import odoo.addons.decimal_precision as dp


class MrpBom(models.Model):

    _inherit = "mrp.bom"

    @api.multi
    def _get_total_cost(self):
        """ Summary field that sums the operation and
        component costs of the BOM """
        for bom in self:
            bom.total_cost = bom.component_cost + bom.op_cost

    @api.multi
    def _get_op_cost(self):
        for bom in self:
            #     BOM's routing's operation costs
            #   +    BOM's lines' operation costs
            # -----------------------------------
            #   = Operation cost for a single BOM
            total_op_cost = sum(
                [line.op_cost_total for line in bom.bom_line_ids]
            ) + sum(
                [op.operation_cost for op in bom.routing_id.operation_ids]
            )

            bom.op_cost = total_op_cost / bom.product_qty

    op_cost = fields.Float(
        compute=_get_op_cost,
        string='Unit Operation Cost',
        help='Contains the combined operation costs of all sub-assemblies, '
             'for one produced unit',
    )
    total_cost = fields.Float(
        compute=_get_total_cost,
        digits=dp.get_precision('Product Price'),
        string="Unit Total Cost",
        help='Component and operations costs combined '
             'for all parts and sub-assemblies, for one produced unit'
    )
