from odoo import api, models
import logging

_logger = logging.getLogger(__name__)


class MultiLevelMrp(models.TransientModel):

    _inherit = "mrp.multi.level"

    @api.model
    def _prepare_mrp_move_data_from_stock_move(self, product_mrp_area, move, direction="in"):
        move_data = super()._prepare_mrp_move_data_from_stock_move(
            product_mrp_area=product_mrp_area,
            move=move,
            direction=direction
        )

        ignore_production = product_mrp_area.mrp_area_id.ignore_production_orders
        production = move_data.get("production_id", False)

        if production and ignore_production:
            _logger.info("Ignoring production orders in MRP multi level computations")
            return {}

        return move_data
