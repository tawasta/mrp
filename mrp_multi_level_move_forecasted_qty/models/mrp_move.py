from odoo import fields, models


class MrpMove(models.Model):
    # 1. Private attributes
    _inherit = "mrp.move"

    # 2. Fields declaration
    forecasted_qty = fields.Float(compute="_compute_forecasted_qty", store=False)

    # 3. Default methods

    # 4. Compute and search fields, in the same order that fields declaration
    def _compute_forecasted_qty(self):
        """
        Compute forecasted_qty as product_mrp_area_id.qty_available +
        mrp_qty + mrp_qty of all previous moves on the same product_mrp_area_id
        """
        for move in self:
            prev_mrp_qty = 0
            for product_mrp_area_move in move.product_mrp_area_id.mrp_move_ids:
                if move == product_mrp_area_move:
                    break
                prev_mrp_qty += product_mrp_area_move.mrp_qty
            move.forecasted_qty = (
                move.product_mrp_area_id.qty_available + prev_mrp_qty + move.mrp_qty
            )
