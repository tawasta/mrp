from odoo import models


class MrpProduction(models.Model):

    _inherit = "mrp.production"

    def _compute_finished_product_move_cost(self, raw_material_move_ids):
        res = super(MrpProduction, self)._compute_finished_product_move_cost(
            raw_material_move_ids=raw_material_move_ids,
        )

        # Calculate work center costs, if any
        if self.workorder_ids:
            operation_cost = 0

            for work_order in self.workorder_ids:
                work_center = work_order.workcenter_id
                if not work_center.service_product_id:
                    continue

                # TODO: allow using real duration
                duration = work_order.duration_expected / 60
                unit_cost = work_center.service_product_id.standard_price

                operation_cost += duration * unit_cost

            res += operation_cost

        return res
