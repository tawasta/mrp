# -*- coding: utf-8 -*-

from odoo import api, models
from odoo import _
from odoo.exceptions import ValidationError


class MrpProduction(models.Model):

    _inherit = 'mrp.production'

    @api.multi
    def post_inventory(self):
        # Override post inventory to use correct FIFO price on stock.quant

        raw_material_moves = dict()
        finished_product_moves = dict()

        for order in self:
            moves_to_do = order.move_raw_ids.filtered(
                lambda x: x.state not in ('done', 'cancel'))

            moves_to_finish = order.move_finished_ids.filtered(
                lambda x: x.state not in ('done', 'cancel')
            )

            raw_material_moves[order.id] = moves_to_do
            finished_product_moves[order.id] = moves_to_finish

        res = super(MrpProduction, self).post_inventory()

        # Fix the quant prices to match the used raw materials
        for order in self:
            if order.id not in raw_material_moves:
                msg = _('Could not find raw material moves.')
                raise ValidationError(msg)

            if order.id not in finished_product_moves:
                msg = _('Could not find finished product moves.')
                raise ValidationError(msg)

            raw_material_move_ids = raw_material_moves[order.id]
            finished_product_move_id = finished_product_moves[order.id]

            if len(finished_product_move_id) > 1:
                msg = _('Multiple finished products not supported.')
                raise ValidationError(msg)

            if finished_product_move_id.product_id.cost_method == 'real':
                # Calculate the real cost
                real_cost = self._compute_finished_product_move_cost(
                    raw_material_move_ids,
                )

                qty = finished_product_move_id.product_uom_qty
                product_cost = real_cost / qty

                finished_product_move_id.sudo().quant_ids.cost = product_cost

        return res

    def _compute_finished_product_move_cost(self, raw_material_move_ids):
        # Calculate the real cost
        real_cost = 0

        # Loop through all the moves
        for raw_material_move_id in raw_material_move_ids:
            quant_cost = 0

            # Loop through each moved quant in th move
            for quant in raw_material_move_id.quant_ids:
                quant_cost += quant.inventory_value

            real_cost += quant_cost

        return real_cost
